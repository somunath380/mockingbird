from db.connection import get_session
from db.models import User
from sanic.log import logger

class QueryDB(object):
    def __init__(self, 
                 Table: object, 
                 filter_by_config: dict=None,
                 query_type: str=None,
                 **kwargs
                 ):
        if kwargs.get("logger"):
            self.logger: object = kwargs.get("logger")
        else:
            self.logger = logger
        self.table = Table
        self.query_type = query_type
        self.filter_by_config = filter_by_config
    
    def _get_session(self):
        self.logger.info("get session")
        self.session = get_session()
    
    def _terminate_session(self):
        self.logger.info("session terminated")
        self.session.close()
    
    def _rollback_session(self):
        self.logger.info("session rollbacked")
        self.session.rollback()
    
    def _commit_session(self):
        self.logger.info("session commited")
        self.session.commit()
    
    def _execute(self, query_obj=None, data=None):
        self.logger.info("executing query")
        try:
            if self.query_type == "all":
                self.logger.info("get all")
                return query_obj.all()
            elif self.query_type == "first":
                self.logger.info("get first")
                return query_obj.first()
            elif self.query_type == "insert":
                self.logger.info("insert data")
                data_obj = self.table(**data)
                self.session.add(data_obj)
                self._commit_session()
            elif self.query_type == "delete":
                self.logger.info("deleting data")
                query_obj.delete()
            else:
                self.logger.info("invalid command given")
                raise Exception("invalid command given")
        except Exception as exe:
            self._rollback_session()
            self.logger.info(f"error occured {exe}")
        finally:
            self._terminate_session()

    def get(self):
        self._get_session()
        self.logger.info("creating query object")
        query = self.session.query(self.table).filter_by(**self.filter_by_config)
        return self._execute(query)
    
    def get_all_users(self):
        self._get_session()
        self.logger.info("creating query object")
        query = self.session.query(User)
        return self._execute(query)

    def insert(self, data):
        self._get_session()
        self.logger.info("creating query object")
        self._execute(**data)

    def delete(self):
        self._get_session()
        self.logger.info("creating query object")
        query = self.session.query(self.table).filter_by(**self.filter_by_config)
        self._execute(query)
