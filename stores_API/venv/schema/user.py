from ma import ma
from marshmallow import pre_dump
from models.user import UserModel 


class UserSchema(ma.SQLAlchemyAutoSchema):
    
    class Meta: 
        model = UserModel
        dump_only = ("id", "confirmation",)
        load_only = ("password","email",) 
        load_instance = True
    
    @pre_dump
    def _pre_dump(self, user:UserModel):
        user.confirmation =[user.most_recent_confirmation]
        return user