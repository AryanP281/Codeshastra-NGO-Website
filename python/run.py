from flask import Flask, request, render_template, redirect, url_for
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, Boolean

app = Flask(__name__)

engine = create_engine("sqlite:///needyPeople.db",echo=True)
meta = MetaData()

needy = Table("n_people", meta, 
Column("id", Integer, primary_key=True),
Column("name", String),
Column("age", Integer),
Column("sex", String),
Column("bg", String),
Column("disability", String),
Column("loc", String)
)

ngos = Table("ngos", meta, 
Column("id", Integer, primary_key=True),
Column("name", String),
Column("loc", String),
Column("dons_rcv", Integer),
Column("hlpd", Integer)
)

ndy = needy.select()
conn = engine.connect()
res = conn.execute(ndy)

needy_profiles_count = list(res).__len__()

s = ngos.select()
res = conn.execute(s)
registered_ngos =  list(res).__len__()

@app.route("/",methods=["GET","POST"])
def home() :
        return render_template("index.html")

@app.route("/createneedyprofile", methods=["GET", "POST"])
def create_needy_profile() :
    if request.method == "POST" :
        global name, age, dl, needy_profiles_count
        needy_profiles_count += 1
        profile = [ request.form["name"],
        request.form["age"],
        request.form["gender"],
        request.form["bldgrp"],
        request.form["phydis"],
        request.form["loc"] ]
        add_to_needy_database(profile)
        return render_template("success.html")
    else :
         return render_template("needy_profile.html")

@app.route("/registerngo", methods=["GET", "POST"])
def register_ngo() :
    if request.method == "POST" :
        global registered_ngos
        registered_ngos += 1
        data = [ request.form["name"],
        request.form["loc"],
        request.form["don"],
        request.form["nop"]
        ]

        ins_op = ngos.insert().values(id=registered_ngos,name=data[0],loc=data[1],dons_rcv=data[2],hlpd=data[3])
        conn = engine.connect()
        res = conn.execute(ins_op) 

        return redirect("/")
    else :
        return render_template("RegisterNgo.html")

@app.route("/locatengo", methods=["GET", "POST"])
def locate_ngo() :
    if request.method == "POST" :
        return redirect("/")
    else :
        return render_template("search.html")

@app.route("/ngolist")
def ngo_list() :
    s = ngos.select()
    conn = engine.connect()
    res = conn.execute(s)

    lst = []
    for e in res :
        lst.append(list(e)[1])

    return render_template("ngo_list.html", ngos=lst)

@app.route("/searchbyloc", methods=["GET", "POST"])
def search_by_loc() :
    if request.method == "POST" :
        url = f"/ngoprofile/" + str(request.form["ngo"])
        return redirect(url)
    else :
        return render_template("search.html")

@app.route("/needylist")
def needy_list() :
    s = ndy.select()
    conn = engine.connect()
    res = conn.execute(s)

    lst = []
    for e in res :
        lst.append(list(e)[1])

    return render_template("needy_list.html", names=lst)

@app.route("/needyprofile/<name>")
def needy_profile(name) :
    s = ndy.select().where(ndy.c.name == name)
    conn = engine.connect()
    prof = list(conn.execute(s))  

    return render_template("needy_profile_display.html", name=prof[0][1], age=prof[0][2], sex=prof[0][3], bg=prof[0][4], disability=prof[0][5], loc=prof[0][6])

@app.route("/ngoprofile/<name>", methods=["GET", "POST"])
def ngo_profile(name):
    s = ngos.select().where(ngos.c.name == name)
    conn = engine.connect()
    prof = list(conn.execute(s))
    
    if request.method == "GET" :
        return render_template("ngo_profile.html", name = prof[0][1], loc=prof[0][2], dons=prof[0][3], hlpd=prof[0][4])
    else :
        return redirect(f"/donate/{prof[0][1]}")


@app.route("/donate/<name>", methods=["GET","POST"])
def donate(name) :
    s = ngos.select().where(ngos.c.name == name)
    conn = engine.connect()
    prof = list(conn.execute(s))
    
    if request.method == "POST" :
        upd = ngos.update().where(ngos.c.name == name).values(dons_rcv=int(prof[0][3]) + int(request.form["mtrans"]))
        conn.execute(upd)
        return redirect("/")
    else :
        return render_template("payment_details.html", ngo=name)

@app.route("/debug")
def dbg() :
    return f"{needy_profiles_count}"


def add_to_needy_database(data) :
    ins_op = needy.insert().values(id=needy_profiles_count,name=data[0],age=data[1],sex=data[2],bg=data[3],disability=data[4],loc=data[5])
    conn = engine.connect()
    res = conn.execute(ins_op)  


if(__name__ == "__main__") :
    app.run(debug=True)