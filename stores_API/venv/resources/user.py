from functools import partial
import traceback
from flask_restful import Resource, reqparse
from flask import request  
from werkzeug.security import safe_str_cmp 
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required, 
    get_jwt_identity, 
    get_jwt
)
from marshmallow import INCLUDE, EXCLUDE  
from schema.user import UserSchema 
from models.user import UserModel
from blacklist import BLACKLIST   
from typing import Dict, List 
from libs.mailgun import MailGunException
from libs.strings import gettext 
from models.confirmation import ConfirmationModel 


user_schema = UserSchema(unknown=INCLUDE)
 

class UserRegister(Resource): 
    @classmethod
    def post(cls): 
            user= user_schema.load(request.get_json())      
        
            if UserModel.find_by_username(user.username):
                return {"message": gettext("user_username_exists")}, 400 
            
            if UserModel.find_by_email(user.email):
                return {"message": gettext("user_email_exists")}, 400 

            try:
                user.save_to_db() 
                confirmation = ConfirmationModel(user.id)
                confirmation.save_to_db()
                user.send_confirmation_email() 
                return {"message": gettext("user_registered")}, 200 
            except MailGunException as e:
                user.delete_from_db()
                return {"message": str(e)}, 500
            
            except: 
                traceback.print_exc()
                user.delete_from_db()
                return {"message": gettext("user_error_creating")}, 500 

            

class User(Resource): 
    @classmethod
    def get(cls, user_id: int): 
        user = UserModel.find_by_id(user_id)
        if not user: 
            return {'message': gettext("user_not_found")}, 404 
        return user_schema.dump(user), 200

    @classmethod 
    def delete(cls, user_id: int): 
        user = UserModel.find_by_id(user_id)
        if not user: 
            return {'message': gettext("user_not_found")}, 404 
        user.delete_from_db() 
        return {'message': gettext("user_deleted")}, 200 


class UserLogin(Resource):

    @classmethod 
    def post(cls): 
        user_json = request.get_json()
        user_data = user_schema.load(user_json, partial=("email",))
      
        user = UserModel.find_by_username(user_data.username) 

        if user and safe_str_cmp(user.password, user_data.password): 
            confirmation = user.most_recent_confirmation
            if confirmation and confirmation.confirmed: 
                access_token = create_access_token(identity=user.id, fresh=True)
                refresh_token = create_refresh_token(user.id) 
                return {
                    'access_token' : access_token, 
                    'refresh_token': refresh_token
                        }, 200 
            return {"message": gettext("user_not_confirmed").format(user.username)}, 200
        return {'message': gettext("user_invalid_credentials")}, 400

class UserLogout(Resource):
    @classmethod
    @jwt_required(refresh=False)
    def post(cls): 
        jti = get_jwt()["jti"] 
        user_id = get_jwt_identity()
        BLACKLIST.add(jti)
        return{'message': gettext("user_logged_out").format(user_id=user_id)}, 200 


class TokenRefresh(Resource): 
    @classmethod
    @jwt_required(refresh=True)
    def post(cls): 
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200 
        

