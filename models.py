from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Party(db.Model):

    __tablename__ = "party"
    id = db.Column(db.Integer, primary_key=True)
    partyid = db.Column(db.String, nullable=False)
    partyname = db.Column(db.String, nullable=False, unique=True)


class LGA(db.Model):
    __tablename__ = "lga"
    uniqueid = db.Column(db.Integer, primary_key=True)
    lga_id = db.Column(db.Integer, nullable=False, unique=True)
    lga_name = db.Column(db.String, nullable=False)
    state_id = db.Column(db.Integer, nullable=False)
    lga_description = db.Column(db.String, nullable=True)


class Ward(db.Model):
    __tablename__ = "ward"
    uniqueid = db.Column(db.Integer, primary_key=True, unique=True)
    ward_id = db.Column(db.Integer, nullable=False)
    ward_name = db.Column(db.String, nullable=True)
    lga_id = db.Column(db.Integer, db.ForeignKey("lga.lga_id"))
    ward_description = db.Column(db.String, nullable=True)
    entered_by_user = db.Column(db.String, nullable=True)
    date_entered = db.Column(db.String, nullable=True)
    user_ip_address = db.Column(db.String, nullable=True)


class PolingUnits(db.Model):
    __tablename__ = "polling_unit"
    uniqueid = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    polling_unit_id = db.Column(db.Integer, nullable=False)
    ward_id = db.Column(db.Integer, nullable=False)
    lga_id = db.Column(db.Integer, db.ForeignKey("lga.lga_id"), nullable=False)
    uniquewardid = db.Column(db.Integer, db.ForeignKey("ward.uniqueid"), nullable=False)
    polling_unit_number = db.Column(db.String, nullable=False)
    polling_unit_name = db.Column(db.String, nullable=True)
    polling_unit_description = db.Column(db.String, nullable=True)


class Announced_lga_results(db.Model):
    __tablename__ = "announced_lga_results"
    result_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lga_name = db.Column(db.Integer, db.ForeignKey("lga.lga_id"), nullable=False)
    party_abbreviation = db.Column(db.String, nullable=False)
    party_score = db.Column(db.Integer, nullable=False)
    entered_by_user = db.Column(db.String, nullable=False)
    date_entered = db.Column(db.String, nullable=False)
    user_ip_address = db.Column(db.String, nullable=False)


class Announced_pu_results(db.Model):
    __tablename__ = "announced_pu_results"
    result_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    polling_unit_uniqueid = db.Column(db.Integer, db.ForeignKey("polling_unit.uniqueid"), nullable=False)
    party_abbreviation = db.Column(db.String, db.ForeignKey("party.partyname"), nullable=False)
    party_score = db.Column(db.Integer, nullable=False)
    entered_by_user = db.Column(db.String, nullable=False)
    date_entered = db.Column(db.String, nullable=False)
    user_ip_address = db.Column(db.String, nullable=False)
