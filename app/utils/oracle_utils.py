from utils.database import execute_query, get_connection
from typing import List, Dict, Any, Optional

class OracleUtils:
    @staticmethod
    def execute_procedure(procedure_name: str, params: Dict[str, Any] = None) -> Optional[List[Dict[str, Any]]]:
        """Oracle 저장 프로시저 실행"""
        params_str = ", ".join([f":{key}" for key in params.keys()]) if params else ""
        query = f"BEGIN {procedure_name}({params_str}); END;"
        
        with get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, params or {})
                conn.commit()
                
                # 결과 반환이 있는 경우 (REF CURSOR)
                if cursor.description:
                    result = cursor.fetchall()
                    columns = [col[0] for col in cursor.description]
                    return [dict(zip(columns, row)) for row in result]
                return None
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()
    
    @staticmethod
    def use_pagination(query: str, page: int, page_size: int, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Oracle 페이지네이션 (OFFSET-FETCH) - Oracle 12c 이상용"""
        paginated_query = f"""
        {query}
        OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY
        """
        
        offset = (page - 1) * page_size
        params = params or {}
        params.update({"offset": offset, "limit": page_size})
        
        return execute_query(paginated_query, params)
    
    @staticmethod
    def use_rownum_pagination(query: str, page: int, page_size: int, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Oracle ROWNUM 기반 페이지네이션 (오래된 버전용)"""
        paginated_query = f"""
        SELECT *
        FROM (
            SELECT a.*, ROWNUM rn
            FROM ({query}) a
            WHERE ROWNUM <= :max_row
        )
        WHERE rn > :min_row
        """
        
        min_row = (page - 1) * page_size
        max_row = page * page_size
        
        params = params or {}
        params.update({"min_row": min_row, "max_row": max_row})
        
        return execute_query(paginated_query, params)
    
    @staticmethod
    def handle_clob(clob_data):
        """CLOB 데이터 처리"""
        if clob_data is None:
            return None
        return clob_data.read()
    
    @staticmethod
    def handle_blob(blob_data):
        """BLOB 데이터 처리"""
        if blob_data is None:
            return None
        return blob_data.read()
    
    @staticmethod
    def get_sequence_nextval(sequence_name: str) -> int:
        """시퀀스의 다음 값 가져오기"""
        query = f"SELECT {sequence_name}.NEXTVAL FROM DUAL"
        result = execute_query(query)
        return result[0]['NEXTVAL'] if result else None
    
    @staticmethod
    def get_current_date():
        """Oracle 서버의 현재 날짜/시간 가져오기"""
        query = "SELECT SYSDATE FROM DUAL"
        result = execute_query(query)
        return result[0]['SYSDATE'] if result else None