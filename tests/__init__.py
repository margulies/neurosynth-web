from mock import MagicMock, Mock, patch
import re
import inspect


from flask_testing import TestCase as Base
from nsweb.core import create_app, register_blueprints, db
from nsweb.models import Study, Peak, Feature, Frequency

#this is here for now. Needs to be replaced with the factory later!
from nsweb.helpers import database_builder
from tests.settings import DATA_DIR, PICKLE_DATABASE, FEATURE_DATABASE, PROD_PICKLE_DATABASE, IMAGE_DIR, SQLALCHEMY_DATABASE_URI, DEBUG, DEBUG_WITH_APTANA
from flask_sqlalchemy import BaseQuery

class TestCase(Base):
    def create_app(self):
        '''creates the app and a sqlite database in memory'''
        app = create_app(database_uri=SQLALCHEMY_DATABASE_URI, debug=DEBUG, aptana=DEBUG_WITH_APTANA)
        
        #creates and registers blueprints in nsweb.blueprints
        import nsweb.blueprints.studies
        import nsweb.blueprints.features
        import nsweb.blueprints.images
        #loads blueprints
        register_blueprints()

        self.client=app.test_client()
        return app

    def setUp(self):
        '''creates tables'''
        db.create_all()

    def tearDown(self):
        '''drops tables'''
        db.session.remove()
        db.drop_all()
    
    def populate_db(self,images=True):
        '''populates the database with Studies, Peaks, Features, and Frequencies. Image location as well if images is True'''
        dataset = database_builder.read_pickle_database(data_dir=DATA_DIR, pickle_database=PICKLE_DATABASE)
        (feature_list,feature_data) = database_builder.read_features_text(data_dir=DATA_DIR,feature_database=FEATURE_DATABASE)
        if images:
            feature_dict = database_builder.add_features(db,feature_list,IMAGE_DIR)
        else:
            feature_dict = database_builder.add_features(db,feature_list)
        database_builder.add_studies(db, dataset, feature_list, feature_data, feature_dict)
        
    def get_prod_data_fields(self):
        fields = database_builder.read_pickle_database(DATA_DIR, PROD_PICKLE_DATABASE)[0].keys()
        fields = [x for x in fields if not re.search(r'_id', x) and x !='id']
        return fields
    
    def assert_model_equality(self,models, query_models, additional_fields=[]):
        '''This gets the model parameters from init then iterates over the list comparing the models. This may not be the best way, but it works. Also this was supposed to be a test generator, but this is an extension of unittest.TestCase so those aren't allowed. Protip: It's recursive'''
        assert len(models)==len(query_models)
        assert len(models) > 0
        fields = self.get_attributes(models[0])
        fields.extend(additional_fields)
        for x in range(len(models)):
            for y in fields:
                attr1=getattr(models[x], y)
                attr2=getattr(query_models[x], y)
                if isinstance(attr1, BaseQuery):
                    attr1=attr1.all()
                if isinstance(attr2, BaseQuery):
                    attr2=attr2.all()
                if isinstance(attr1, list):
                    self.assert_model_equality(attr1, attr2)
                else:
                    assert attr1 == attr2

    def assert_model_contains_fields(self,model, fields):
        attributes = self.get_attributes(model)
        for x in fields:
            if x not in attributes:
                assert getattr(model, x) is not None
            else:
                assert True
            
            
    def get_attributes(self, model):
        fields = vars(model).keys()
        fields = [a for a in fields if a[0] !='_' and a != 'id']
        return fields