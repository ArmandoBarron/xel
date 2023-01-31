class Config(object):
  DEBUG = False
  TESTING = False
  THREADED = True

class ProductionConfig(Config):
  pass

class DevelopmentConfig(Config):
  DEBUG = True

class TestingConfig(Config):
  TESTING = True
