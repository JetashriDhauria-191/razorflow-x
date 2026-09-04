import sys
import backend.database as _bd
sys.modules['database'] = _bd

engine = _bd.engine
SessionLocal = _bd.SessionLocal
Base = _bd.Base
get_db = _bd.get_db
