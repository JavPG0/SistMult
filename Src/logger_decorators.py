import functools
import time
import logging

def log_execution(logger):
    """
    Decorador que registra automáticamente la ejecución de una función.
    
    Captura:
    - Cuándo inicia la función
    - Cuánto tiempo tarda
    - Si termina exitosamente o con error
    - Parámetros que recibió (opcional)
    
    Para usarlo:
        @log_execution(logger)
        def mi_funcion(param1, param2):
            # tu código
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"Inicio de la función '{func.__name__}'", extra = {'extra_data': {'function': func.__name__, 'args_len': len(args), 'kwargs_keys': list(kwargs)}})
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"Inicio de la función '{func.__name__}'", extra = {'extra_data': {'function': func.__name__, 'args_len': len(args), 'kwargs_keys': list(kwargs)}})
                
                return result
            
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Error en la función '{func.__name__}': {e}", extra = {'extra_data': {'function': func.__name__, 'args_len': len(args), 'kwargs_keys': list(kwargs), 'error': str(e)}}, exc_info = True)

                raise

        return wrapper
        
    return decorator
