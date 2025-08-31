class DevelopmentConfig():
    SQLALCHEMY_DATABASE_URI = 'mysql://root:@localhost/dbmundo'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'dbmundo'
    SECRET_KEY = '1234'
    UPLOADED_IMAGES_DEST = 'static/uploads/images'
    UPLOADED_FILES_DEST = 'static/uploads/files'


config = {
    'development': DevelopmentConfig
    }