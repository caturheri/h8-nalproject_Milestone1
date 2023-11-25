from os import environ
from flask import Flask
from flask_restx import Api, Resource, fields, reqparse
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.app_context().push()
api = Api(app, version='1.0', title='Learning Milestones API', description='CRUD operations for learning milestones', doc='/docs', default='Milestone')

class MilestoneModel(db.Model):
    __tablename__ = 'milestones'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    completed = db.Column(db.Boolean, default=False)

db.create_all()

milestone_model = api.model('Milestone', {
    'id': fields.Integer(readonly=True, description='The milestone identifier'),
    'title': fields.String(required=True, description='The milestone title'),
    'description': fields.String(required=True, description='Description of the milestone'),
    'completed': fields.Boolean(description='Status of milestone completion')
})

parser = reqparse.RequestParser()
parser.add_argument('title', type=str, help='Title of the milestone')
parser.add_argument('description', type=str, help='Description of the milestone')
parser.add_argument('completed', type=bool, help='Status of milestone completion')

@api.route('/milestones')
class MilestoneList(Resource):
    @api.marshal_list_with(milestone_model)
    def get(self):
        """List all milestones"""
        milestones = MilestoneModel.query.all()
        return milestones

    @api.expect(milestone_model)
    @api.marshal_with(milestone_model, code=201)
    def post(self):
        """Create a new milestone"""
        args = parser.parse_args()
        milestone = MilestoneModel(
            title=args['title'],
            description=args['description'],
            completed=args['completed']
        )
        db.session.add(milestone)
        db.session.commit()
        return milestone, 201

@api.route('/milestones/<int:milestone_id>')
class Milestone(Resource):
    @api.marshal_with(milestone_model)
    def get(self, milestone_id):
        """Get details of a specific milestone"""
        milestone = MilestoneModel.query.get(milestone_id)
        if milestone is None:
            api.abort(404, f"Milestone {milestone_id} not found")
        return milestone

    @api.expect(milestone_model)
    @api.marshal_with(milestone_model)
    def put(self, milestone_id):
        """Update a milestone"""
        milestone = MilestoneModel.query.get(milestone_id)
        if milestone is None:
            api.abort(404, f"Milestone {milestone_id} not found")

        args = parser.parse_args()
        milestone.title = args['title']
        milestone.description = args['description']
        milestone.completed = args['completed']

        db.session.commit()
        return milestone

    @api.response(204, 'Milestone deleted')
    def delete(self, milestone_id):
        """Delete a milestone"""
        milestone = MilestoneModel.query.get(milestone_id)
        if milestone is None:
            api.abort(404, f"Milestone {milestone_id} not found")

        db.session.delete(milestone)
        db.session.commit()
        return '', 204

if __name__ == '__main__':
    app.run(debug=True)