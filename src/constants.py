from enum import Enum


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

SQL_ALCHEMY_NAMING_CONVENTION = {
    # Indexes: idx_tablename_columnname(s)
    "ix": "idx_%(table_name)s_%(column_0_label)s",
    
    # Unique constraints: uq_tablename_columnname(s) 
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    
    # Check constraints: ck_tablename_constraintname
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    
    # Foreign keys: fk_tablename_columnname
    "fk": "fk_%(table_name)s_%(column_0_name)s",
    
    # Primary keys: pk_tablename
    "pk": "pk_%(table_name)s",
}
