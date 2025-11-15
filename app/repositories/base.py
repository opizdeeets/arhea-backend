from typing import Any, Mapping, Optional, TypeVar, Generic
from collections.abc import Sequence as Seq
from sqlalchemy import inspect
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.orm.interfaces import ORMOption
from sqlalchemy.exc import IntegrityError
from app.core.errors import DomainError



T = TypeVar("T", bound=DeclarativeMeta)


class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: type[T]):
        self.session = session
        self.model = model

    def _integrity_code_message(self, pgcode: str | None) -> tuple[str, int, str]:
        code_map = {
            "23505": ("unique_violation", 409, "unique constraint violated"),
            "23503": ("foreign_key_violation", 409, "foreign key constraint violated"),
            "23502": ("not_null_violation", 400, "null value in column violates not-null constraint"),
            "23514": ("check_violation", 400, "check constraint violated"),
        }
        return code_map.get(pgcode, ("integrity_error", 409, "integrity constraint violated"))

        

    async def _raise_integrity(self, e: IntegrityError, operation: str, payload: dict):
        orig = getattr(e, "orig", None); diag = getattr(orig, "diag", None)
        pgcode = getattr(orig, "pgcode", None)
        constraint = getattr(diag, "constraint_name", None) or getattr(orig, "constraint_name", None)

                
        details = {
            "model" : self.model.__name__,
            "operation" : operation, **payload,
            "pgcode" : pgcode, 
            "constraint" : constraint,
        }         
        code, status, msg = self._integrity_code_message(pgcode)
        await self.session.rollback() 
        raise DomainError(code, msg, status=status, details=details, cause=e)


    def _build_pk_clause(self, id_or_dict: Any):
        pks = inspect(self.model).primary_key
        if len(pks) == 1:
            return pks[0] == id_or_dict
        
        if not isinstance(id_or_dict, Mapping): 
            raise TypeError("Composite primary key expects a dict with key:value")
        
        clauses = []
        for col in pks:
            key = col.key
            if key not in id_or_dict:
                raise KeyError(f"Missing key part '{key}' for composite PK")        
            clauses.append(col == id_or_dict[key])

        return sa.and_(*clauses)


    async def get(self, id_or_dict: object, options: Seq[ORMOption] | None = None) -> T | None:
        stmt = sa.select(self.model).where(self._build_pk_clause(id_or_dict))
        if options:
            stmt = stmt.options(*options)
        result = await self.session.execute(stmt)
        result = result.unique()
        return result.scalar_one_or_none()
    

    async def list(self, 
        filters: Optional[Mapping[str, Any]] = None, 
        order_by: Optional[Seq[str]] = None, 
        limit: Optional[int] = None, 
        options: Seq[ORMOption] | None = None,
        ) -> list[T]:

        stmt = sa.select(self.model)

        cols = {c.key: getattr(self.moу, c.key) for c in inspect(self.model).mapper.columns}

        conditions = []

        if filters:
            for k,v in filters.items():
                if k not in cols:
                    raise ValueError(f"Invalid filter field: {k}")
                if v is None:
                    continue
                if isinstance(v, Seq) and not isinstance(v, (str, bytes, bytearray)):
                    if len(v) == 0:
                        conditions.append(sa.false())
                    else:    
                        conditions.append(cols[k].in_(v))
                else:
                    conditions.append(cols[k] == v)

        if conditions:
            stmt = stmt.where(sa.and_(*conditions))       

        if order_by:
            orders_expr: list[Any] = []
            for name in order_by:
                desc = name.startswith("-")
                field = name[1:] if desc else name
                if field not in cols: raise ValueError(f"Invalid order_by: {field}")
                expr = cols[field].desc() if desc else cols[field]
                orders_expr.append(expr)
            if orders_expr:                   
                stmt = stmt.order_by(*orders_expr)

        if limit is not None:
            if limit <= 0 or limit > 100: raise ValueError("limit must be 1..100")
            stmt = stmt.limit(limit)

        if options:
            stmt = stmt.options(*options)

        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def exists(self, filters: Optional[Mapping[str, Any]] = None) -> bool:
        cols = {c.key: getattr(self.model, c.key) for c in inspect(self.model).mapper.columns}

        conditions = []
        inner = sa.select(sa.literal(1)).select_from(self.model)
        if filters:
            for k,v in filters.items():
                if k not in cols:
                    raise ValueError(f"Invalid filter field: {k}")
                if v is None:
                    continue
                if isinstance(v, Seq) and not isinstance(v, (str, bytes, bytearray)):
                    if len(v) == 0:
                        conditions.append(sa.false())
                    else:    
                        conditions.append(cols[k].in_(v))
                else:
                    conditions.append(cols[k] == v)

        if conditions:
            inner = inner.where(sa.and_(*conditions))
        stmt = sa.select(sa.exists(inner))
        return bool(await self.session.scalar(stmt))


    async def create(self, data: Mapping[str, Any]) -> T:
        obj = self.model(**data)
        try:
            self.session.add(obj)
            await self.session.flush()
        except IntegrityError as e: await self._raise_integrity(e, "create", {"data_keys" : list(data.keys())})
        return obj
    

    async def update(self, id: Any, data: Mapping[str, Any]) -> Optional[T]:
        obj = await self.get(id)
        if obj is None:
            return None
        for k,v in data.items():
            setattr(obj, k,v)
        try:    
            await self.session.flush()    
        except IntegrityError as e: await self._raise_integrity(e, "update", {"id": id, "data_keys": list(data.keys())})    
        return obj


    async def delete(self, id: Any) -> bool:
        obj = await self.get(id)
        if obj is None:
            return False 
        self.session.delete(obj)
        try:
            await self.session.flush()
        except IntegrityError as e: await self._raise_integrity(e, "delete", {"id": id})
        return True    
    
