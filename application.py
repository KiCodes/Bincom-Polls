from datetime import date

import psycopg2
from flask import Flask, render_template, request


app = Flask(__name__)
ENV = 'voting'

if ENV == 'voting':
    app.debug = True

conn = psycopg2.connect("postgresql://postgres:defence@localhost:5432/postgres")


@app.route('/')
def index():
    # dropdown of polling units with results
    pu_name = conn.cursor()
    pu_name.execute(
        "SELECT DISTINCT polling_unit.uniqueid, polling_unit.polling_unit_name FROM polling_unit "
        "INNER JOIN "
        "announced_pu_results ON polling_unit.uniqueid = announced_pu_results.polling_unit_uniqueid "
        "GROUP BY polling_unit.polling_unit_name, polling_unit.uniqueid; "
    )
    pus = pu_name.fetchall()

    return render_template("index.html", pus=pus)


@app.route("/pu_results", methods=['POST'])
def pu_results():
    # dropdwon value
    name = request.form.get('pu_id')
    if name is not None:
        render_template("error.html")

    # polling unit names for dropdown
    pu_name = conn.cursor()
    pu_name.execute(
        """SELECT DISTINCT polling_unit.uniqueid, polling_unit.polling_unit_name FROM polling_unit 
        INNER JOIN 
        announced_pu_results ON polling_unit.uniqueid = announced_pu_results.polling_unit_uniqueid 
        GROUP BY polling_unit.uniqueid, polling_unit.polling_unit_name"""
    )
    pus = pu_name.fetchall()

    # polling unit heading
    pu_head = conn.cursor()
    pu_head.execute(
        "SELECT DISTINCT polling_unit_name FROM polling_unit WHERE uniqueid = %s", [name]
    )
    pu_heads = pu_head.fetchall()

    # announced pu results
    res = conn.cursor()
    res.execute("SELECT polling_unit_uniqueid , party_abbreviation, SUM(party_score) FROM announced_pu_results WHERE "
                "polling_unit_uniqueid  = %s GROUP BY polling_unit_uniqueid, party_abbreviation ORDER BY SUM("
                "party_score) DESC", [name])
    results = res.fetchall()

    return render_template("index.html", name=name, pus=pus, results=results, pu_heads=pu_heads)


@app.route("/lga")
def lga_page():
    # lga names for dropdown
    lga_names = conn.cursor()
    lga_names.execute(
        """SELECT DISTINCT lga.lga_id, lga.lga_name FROM lga 
        RIGHT JOIN polling_unit ON lga.lga_id = 
        polling_unit.lga_id """
    )
    lgas = lga_names.fetchall()

    return render_template("lgaResult.html", lgas=lgas)


@app.route("/lgaResult", methods=["POST"])
def lga_results():
    # lga names with results
    id_lga = request.form.get('lga_id')

    lga_names = conn.cursor()
    lga_names.execute(
        """SELECT DISTINCT lga.lga_id,
                lga.lga_name FROM ((announced_pu_results 
                INNER JOIN polling_unit ON announced_pu_results.polling_unit_uniqueid = polling_unit.uniqueid) 
                INNER JOIN
                lga ON lga.lga_id = polling_unit.lga_id)"""

    )

    lgas = lga_names.fetchall()

    # party results joined on lga names
    lga_res = conn.cursor()
    lga_res.execute(
        """SELECT DISTINCT announced_pu_results.party_abbreviation, SUM(announced_pu_results.party_score), lga.lga_id,
        lga.lga_name FROM ((announced_pu_results INNER JOIN polling_unit ON announced_pu_results.polling_unit_uniqueid = polling_unit.uniqueid) 
        INNER JOIN
        lga ON lga.lga_id = polling_unit.lga_id) 
        WHERE lga.lga_id = %s 
        GROUP BY announced_pu_results.party_abbreviation, lga.lga_id, lga.lga_name 
        ORDER BY SUM(announced_pu_results.party_score) DESC""",
        [id_lga]
    )
    lga_fin = lga_res.fetchall()

    # lga heading
    pu_head = conn.cursor()
    pu_head.execute(
        "SELECT lga_name FROM lga WHERE lga_id = %s", [id_lga]
    )
    pu_heads = pu_head.fetchall()

    return render_template("lgaResult.html", lga_fin=lga_fin, id_lga=id_lga, lgas=lgas, pu_heads=pu_heads,
                           )


@app.route("/poll")
def poll():
    # fetch lga names
    lga_names = conn.cursor()
    lga_names.execute(
        """SELECT lga.lga_id, lga.lga_name FROM lga"""
    )

    lgas = lga_names.fetchall()

    # fetch ward names
    ward_names = conn.cursor()
    ward_names.execute(
        """SELECT ward.uniqueid, ward.ward_name FROM ward """
    )

    wards = ward_names.fetchall()
    return render_template("newPoll.html", lgas=lgas, wards=wards)


@app.route("/new_poll", methods=["POST"])
def new_poll():
    # add poll unit
    # Get form information.
    poll_name = request.form.get("poll_name")
    poll_description = request.form.get("poll_description")
    poll_id = request.form.get("poll_id")
    ward_id = request.form.get("ward_id")
    ward_unique_id = request.form.get("ward_unique_id")
    lga_id = request.form.get("lga_id")
    polling_unit_number = request.form.get("polling_unit_number")

    # fetch lga names
    lga_names = conn.cursor()
    lga_names.execute(
        """SELECT lga.lga_id, lga.lga_name FROM lga"""
    )

    lgas = lga_names.fetchall()

    # fetch ward names
    ward_names = conn.cursor()
    ward_names.execute(
        """SELECT ward.uniqueid, ward.ward_name FROM ward """
    )

    wards = ward_names.fetchall()
    print(polling_unit_number)

    # checking polling unit number
    p_u_n = conn.cursor()
    poll_un_num = p_u_n.execute(
        """ SELECT polling_unit_number FROM polling_unit WHERE polling_unit_number = %s; """, [polling_unit_number]
    )
    poll_un_num = p_u_n.fetchone()
    print(poll_un_num)

    if poll_un_num is None:
        p_u_n.execute(
            """ INSERT INTO polling_unit 
                (polling_unit_id, ward_id, lga_id, uniquewardid, polling_unit_number, polling_unit_name, polling_unit_description) 
                VALUES 
                (%s, %s, %s, %s, %s, %s, %s)""",
            [poll_id, ward_id, lga_id, ward_unique_id, polling_unit_number, poll_name, poll_description]
        )
        conn.commit()
    elif poll_un_num[0] == polling_unit_number:
        return render_template("newPoll.html", poll_id=poll_id, poll_name=poll_name, poll_description=poll_description,
                               ward_id=ward_id,
                               ward_unique_id=ward_unique_id, lga_id=lga_id, polling_unit_number=polling_unit_number,
                               message="This polling unit number already exists", wards=wards, lgas=lgas)
    else:
        return render_template("add_poll_results.html", message="howw")

    return render_template("add_poll_results.html", message="New polling Unit added")


@app.route("/add_poll_results")
def add_poll_results():
    # poll unit dropdown
    poll_ = conn.cursor()
    poll_.execute(
        """ SELECT DISTINCT uniqueid, polling_unit_name FROM polling_unit"""
    )
    polls = poll_.fetchall()
    return render_template("add_poll_results.html", polls=polls)


@app.route("/sub_poll_results", methods=["POST"])
def submit_poll_results():
    # poll unit dropdown
    poll_ = conn.cursor()
    poll_.execute(
        """ SELECT DISTINCT uniqueid, polling_unit_name FROM polling_unit"""
    )
    polls = poll_.fetchall()

    # ip address
    import socket
    hostname = socket.gethostname()
    Ipadd = socket.gethostbyname(hostname)

    # Get form information.
    poll_uniqueid = request.form.get("poll_uniqueid")
    PDP = request.form.get("PDP")
    DPP = request.form.get("DPP")
    ACN = request.form.get("ACN")
    CDC = request.form.get("CDC")
    JP = request.form.get("JP")
    entered_by = request.form.get("entered_by")

    # insert
    ins = conn.cursor()
    ins.execute(
        """ 
            INSERT INTO announced_pu_results (polling_unit_uniqueid, party_abbreviation, party_score, 
            entered_by_user, date_entered, user_ip_address)
                VALUES
            (%s, 'PDP', %s, %s, %s, %s), 
            (%s, 'DPP', %s, %s, %s, %s), 
            (%s, 'ACN', %s, %s, %s, %s), 
            (%s, 'CDC', %s, %s, %s, %s), 
            (%s, 'JP', %s, %s, %s, %s);
        """, [poll_uniqueid, PDP, entered_by, date.today(), Ipadd,
              poll_uniqueid, DPP, entered_by, date.today(), Ipadd,
              poll_uniqueid, ACN, entered_by, date.today(), Ipadd,
              poll_uniqueid, CDC, entered_by, date.today(), Ipadd,
              poll_uniqueid, JP, entered_by, date.today(), Ipadd, ]
    )
    conn.commit()
    return render_template("add_poll_results.html", message="successful added", polls=polls)


if __name__ == "__main__":
    app.run()
