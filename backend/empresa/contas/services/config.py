# config.py
import os

# Configurações de caminhos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Criar diretório de logs se não existir
os.makedirs(LOGS_DIR, exist_ok=True)

# Configurações de logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'fluxo_caixa': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'fluxo_caixa.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'fluxo_caixa': {
            'handlers': ['fluxo_caixa', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}