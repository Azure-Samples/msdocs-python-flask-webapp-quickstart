import os
from flask import Flask, redirect, render_template, request, url_for, session, flash
import psycopg2
from psycopg2 import pool


app = Flask(__name__)
app.secret_key = 'your secret key2' 

#Make database connection
minconn = 3
maxconn = 10
conn_pool = psycopg2.pool.SimpleConnectionPool(minconn, maxconn, 
                                                user = "postgres",
                                                password = "postgres",
                                                host = "20.203.212.232",
                                                port = "5435",
                                                database = "internprj")


#Function for login page
@app.route('/', methods=['GET', 'POST'])
def index():

    conn = conn_pool.getconn() # connect to database
    cur = conn.cursor() # prepare query
    cur.execute('SELECT * FROM engineer') #get engineer list
    engineers_li = cur.fetchall()

    if request.method == 'POST':
        engineer_id= request.form.get('engineerID') # Get engineer_id

        conn = conn_pool.getconn()
        try:
            cur = conn.cursor() 
            cur.execute('SELECT * FROM engineer WHERE engineer_id = %s', (engineer_id,)) #get engineer with given id
            result = cur.fetchone() 
            if result:
                session['engineer'] = result # load given engineer
                return redirect(url_for('dashboard')) # open dashboard.html
            
            else:
                return redirect(url_for('index')) # redirect to index.html
        finally:
            conn_pool.putconn(conn) # end connection to database
    return render_template('login.html', list_engineers=engineers_li)

#function to save new engineer
@app.route('/save', methods=['POST'])
def save():
    conn = conn_pool.getconn()
    cur = conn.cursor()
    
    if request.method == 'POST':
        engineer_name_new = request.form.get('engineerNameNew') # take inputted engineer name
        cur.execute("INSERT INTO public.engineer(engineer_id, engineer_name) VALUES (DEFAULT, %s)", (engineer_name_new,))
        #inserts engineer with given values taken from params engineer_name_new
        conn.commit()
        flash('Added Successfully')
    return redirect(url_for('index'))

#function to load dashboard with list of engineers
@app.route('/engineers', methods=['GET'])
def engineers():

    conn = conn_pool.getconn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM engineer')
    engineers_li = cur.fetchall()
    conn_pool.putconn(conn)
    return render_template('dashboard.html', list_engineer=engineers_li)

#functino for dashbaord page
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    engineer = session.get('engineer') #get taken engineer
   
    if engineer is None:
        return redirect(url_for('index')) 

    conn = conn_pool.getconn()

    try:
        cur = conn.cursor() # prepare query
        cur.execute('SELECT * FROM mip')
        mips = cur.fetchall()  # take all MIPs
        #take the engineer, steps completed, steps completion
        cur.execute("""
        SELECT E.ENGINEER_NAME, LP.NAME, LPS.LP_STEP_NAME,T.ISCOMPLETE FROM ENGLPSTEPCOMPLETION T
        LEFT JOIN ENGINEER E ON E.ENGINEER_ID = T.ENGINEER_ID
        LEFT JOIN LEARNINGPATHSTEPS LPS ON LPS.LP_STEP_ID = T.LP_STEP_ID
        LEFT JOIN LEARNINGPATH LP ON LP.LEARNINGPATH_ID = LPS.LP_ID
        WHERE E.ENGINEER_ID=%s
        ORDER BY 2 ASC
        """, (engineer[0],) )
        par = cur.fetchall() 

        #take the learningpath, number of steps completed, learningpath completion
        cur.execute("""
        WITH KOD AS (
        SELECT E.ENGINEER_NAME AS NAME,
        LP.NAME AS LPNAME,
        LPS.LP_STEP_NAME AS LPSNAME,
        T.ISCOMPLETE AS RESULT
        FROM ENGLPSTEPCOMPLETION T
        LEFT JOIN ENGINEER E ON E.ENGINEER_ID = T.ENGINEER_ID
        LEFT JOIN LEARNINGPATHSTEPS LPS ON LPS.LP_STEP_ID = T.LP_STEP_ID
        LEFT JOIN LEARNINGPATH LP ON LP.LEARNINGPATH_ID = LPS.LP_ID
        WHERE E.ENGINEER_ID = %s
        ORDER BY 2 ASC
        )
        SELECT KOD.LPNAME,
        COUNT(CASE WHEN KOD.RESULT = 'False' THEN 1 END) AS FalseR,
        COUNT(CASE WHEN KOD.RESULT = 'True' THEN 1 END) AS TrueR,
        CASE WHEN COUNT(CASE WHEN KOD.RESULT = 'False' THEN 1 END) = 0 THEN 'LP Completed'
        ELSE 'LP Not Completed'
        END AS LP_STATUS
        FROM KOD
        GROUP BY KOD.LPNAME
        ORDER BY KOD.LPNAME;
        """, (engineer[0],))
        parComplete = cur.fetchall()

    finally:
        conn_pool.putconn(conn) # database bağlantısını kes

    return render_template('dashboard.html', engineer=engineer, mips=mips, list_par=par, list_complete=parComplete) # dashboard.htmli yükle ve ona engineer(mevcut oturum) ve databaseden elde ettiğimiz mips listesini yükle.

#Function for opening dashboard from login page list
@app.route('/dashboardd/<engineer_id>', methods=['GET'])
def engdash(engineer_id):

    conn = conn_pool.getconn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM engineer WHERE engineer_id = %s', (engineer_id,)) 
    result = cur.fetchone() 

    if result is None:
        return redirect(url_for('index')) 

    conn = conn_pool.getconn()

    try:
        cur = conn.cursor()
        cur.execute('SELECT * FROM mip')
        mips = cur.fetchall()
        cur.execute("""
        SELECT E.ENGINEER_NAME, LP.NAME, LPS.LP_STEP_NAME,T.ISCOMPLETE FROM ENGLPSTEPCOMPLETION T
        LEFT JOIN ENGINEER E ON E.ENGINEER_ID = T.ENGINEER_ID
        LEFT JOIN LEARNINGPATHSTEPS LPS ON LPS.LP_STEP_ID = T.LP_STEP_ID
        LEFT JOIN LEARNINGPATH LP ON LP.LEARNINGPATH_ID = LPS.LP_ID
        WHERE E.ENGINEER_ID=%s
        ORDER BY 2 ASC
        """, (engineer_id,) )
        par = cur.fetchall()

        cur.execute("""
        WITH KOD AS (
        SELECT E.ENGINEER_NAME AS NAME,
        LP.NAME AS LPNAME,
        LPS.LP_STEP_NAME AS LPSNAME,
        T.ISCOMPLETE AS RESULT
        FROM ENGLPSTEPCOMPLETION T
        LEFT JOIN ENGINEER E ON E.ENGINEER_ID = T.ENGINEER_ID
        LEFT JOIN LEARNINGPATHSTEPS LPS ON LPS.LP_STEP_ID = T.LP_STEP_ID
        LEFT JOIN LEARNINGPATH LP ON LP.LEARNINGPATH_ID = LPS.LP_ID
        WHERE E.ENGINEER_ID = %s
        ORDER BY 2 ASC
        )
        SELECT KOD.LPNAME,
        COUNT(CASE WHEN KOD.RESULT = 'False' THEN 1 END) AS FalseR,
        COUNT(CASE WHEN KOD.RESULT = 'True' THEN 1 END) AS TrueR,
        CASE WHEN COUNT(CASE WHEN KOD.RESULT = 'False' THEN 1 END) = 0 THEN 'LP Completed'
        ELSE 'LP Not Completed'
        END AS LP_STATUS
        FROM KOD
        GROUP BY KOD.LPNAME
        ORDER BY KOD.LPNAME;
        """, (engineer_id,))
        parComplete = cur.fetchall()

    finally:
        conn_pool.putconn(conn)

    return render_template('dashboard.html', engineer=result,  mips=mips, list_par=par, list_complete=parComplete)

#Function to open mips.html
@app.route('/mips', methods=['GET'])
def mip_list_link():
    conn = conn_pool.getconn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM mip')
    mips = cur.fetchall()
    return render_template('mips.html', list_mips=mips)


#Function to open paths.html
@app.route('/paths/<mip_id>', methods=['GET'])
def paths(mip_id):
    
    conn = conn_pool.getconn()
    cur = conn.cursor() 
    cur.execute('SELECT * FROM learningpath WHERE mip_id = %s', (mip_id,)) 
    result = cur.fetchall() 
    print(result)
    conn_pool.putconn(conn) 
    return render_template('paths.html', list_mips=result)

#function for pathsteps.html
@app.route('/pathsteps/<learningpath_id>', methods=['GET'])
def pathsteps(learningpath_id):
    
    conn = conn_pool.getconn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM learningpathsteps WHERE lp_id = %s', (learningpath_id,)) 
    result = cur.fetchall() 
    print(result)
    conn_pool.putconn(conn) 
    return render_template('pathsteps.html', list_steps=result)

#function to update an engineer
@app.route('/update/<engineer_id>', methods=['POST'])
def update_engineer(engineer_id):
    if request.method == 'POST':
        engineer_name = request.form['engineer_name']
         
        conn = conn_pool.getconn() 
        cur = conn.cursor()
        cur.execute("""
            UPDATE engineer
            SET engineer_name = %s
            WHERE engineer_id = %s
            """, (engineer_name, engineer_id))

        flash('Engineer Updated Successfully')
        conn.commit()
        return redirect(url_for('index'))

#function to edit an engineer
@app.route('/edit/<engineer_id>', methods = ['POST', 'GET'])
def edit(engineer_id):

    conn = conn_pool.getconn() 
    cur = conn.cursor()
    cur.execute('SELECT * FROM engineer WHERE engineer_id = {0}'.format(engineer_id))
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('edit.html', engineer = data[0])

#function to edit a MIP
@app.route('/edit_mip/<mip_id>', methods = ['POST', 'GET'])
def edit_mip(mip_id):

    conn = conn_pool.getconn() 
    cur = conn.cursor()
    cur.execute('SELECT * FROM mip WHERE mip_id = {0}'.format(mip_id))
    data = cur.fetchall()
    cur.execute('SELECT * FROM learningpath WHERE mip_id = {0}'.format(mip_id))
    path = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('editMIP.html', mip = data[0], learningpath=path)

#function to add a MIP
@app.route('/add_mip/<mip_id>', methods = ['POST', 'GET'])
def add_mip(mip_id):

    conn = conn_pool.getconn() 
    cur = conn.cursor()
    cur.execute('SELECT * FROM mip WHERE mip_id = {0}'.format(mip_id))
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('mipADD.html', mip = data[0])

#Function to update MIP
@app.route('/update_mip/<mip_id>', methods=['POST'])
def update_mip(mip_id):
    if request.method == 'POST':
        mip_name = request.form['mip_name']
         
        conn = conn_pool.getconn() 
        cur = conn.cursor()
        cur.execute("""
            UPDATE mip
            SET mip_name = %s
            WHERE mip_id = %s
            """, (mip_name, mip_id))

        flash('MIP Updated Successfully')
        conn.commit()
        return redirect(url_for('dashboard'))

#Function to save MIP
@app.route('/save_mip', methods=['POST'])
def save_mip():
    conn = conn_pool.getconn()
    cur = conn.cursor()
    
    if request.method == 'POST':
        engineer_mip_new = request.form.get('mipNameNew') #take inputted MIP name
        cur.execute("INSERT INTO public.mip(mip_id, mip_name) VALUES (DEFAULT, %s)", (engineer_mip_new,))
        #inserts mip with given values taken from params new mip ...
        conn.commit()
        flash('Added Successfully')
    return redirect(url_for('dashboard'))

#Function to save a mip
@app.route('/save_mip_list', methods=['POST'])
def save_mip_list():
    conn = conn_pool.getconn()
    cur = conn.cursor()
    
    if request.method == 'POST':
        engineer_mip_new = request.form.get('mipNameNew')
        cur.execute("INSERT INTO public.mip(mip_id, mip_name) VALUES (DEFAULT, %s)", (engineer_mip_new,))
        conn.commit()
        flash('Added Succesfully')
    return redirect(url_for('mip_list_link'))

#Function to delete engineer
@app.route('/delete/<engineer_id>', methods = ['POST','GET'])
def delete(engineer_id):

    conn = conn_pool.getconn() 
    cur = conn.cursor()
    cur.execute('DELETE FROM engineer WHERE engineer_id = {0}'.format(engineer_id))
    conn.commit()
    flash('Engineer Removed Successfully')
    return redirect(url_for('index'))

#Function to delete a mip
@app.route('/delete_mip/<mip_id>', methods = ['POST','GET'])
def delete_mip(mip_id):

    conn = conn_pool.getconn() 
    cur = conn.cursor()
    cur.execute('DELETE FROM mip WHERE mip_id = {0}'.format(mip_id))
    conn.commit()

    return redirect(url_for('dashboard'))

#Funtion to delete a mip
@app.route('/delete_mip_list/<mip_id>', methods = ['POST','GET'])
def delete_mip_list(mip_id):

    conn = conn_pool.getconn() 
    cur = conn.cursor()
    cur.execute('DELETE FROM mip WHERE mip_id = {0}'.format(mip_id))
    conn.commit()

    return redirect(url_for('mip_list_link'))




#function to edit a LP
@app.route('/edit_lp/<learningpath_id>', methods = ['POST', 'GET'])
def edit_lp(learningpath_id):

    conn = conn_pool.getconn() 
    cur = conn.cursor()
    cur.execute('SELECT * FROM learningpath WHERE learningpath_id = {0}'.format(learningpath_id))
    data = cur.fetchall()
    cur.close()
    return render_template('editlp.html', learningpath = data[0])

#function to update a Learningpath
@app.route('/update_lp/<learningpath_id>', methods=['POST'])
def update_lp(learningpath_id):
    if request.method == 'POST':
        lp_name = request.form['name']
         
        conn = conn_pool.getconn() 
        cur = conn.cursor()
        cur.execute("""
            UPDATE learningpath
            SET name = %s
            WHERE learningpath_id = %s
            """, (lp_name, learningpath_id))

        flash('LP Updated Successfully')
        conn.commit()
        return redirect(url_for('dashboard'))

#function to save new learningpath
@app.route('/save_lp/<mip_id>', methods=['POST'])
def save_lp(mip_id):
    conn = conn_pool.getconn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM learningpath WHERE mip_id = {0}'.format(mip_id))
    data = cur.fetchall()
    cur.execute('SELECT * FROM mip WHERE mip_id = {0}'.format(mip_id))
    mip = cur.fetchall()

    if request.method == 'POST':
        lp_name_new = request.form.get('name') # take inputted engineer name
        cur.execute("INSERT INTO public.learningpath(learningpath_id, mip_id, name) VALUES (DEFAULT, %s, %s)", (mip_id, lp_name_new,))
        #inserts engineer with given values taken from params engineer_name_new
        conn.commit()
        flash('Added Successfully')
    return redirect(url_for('dashboard'))

#Function to delete a learningpath
@app.route('/delete_lp/<learningpath_id>', methods = ['POST','GET'])
def delete_lp(learningpath_id):

    conn = conn_pool.getconn() 
    cur = conn.cursor()
    cur.execute('DELETE FROM learningpath WHERE learningpath_id = {0}'.format(learningpath_id))
    conn.commit()
    return render_template('paths.html')


# MAIN FONKSİYONUMUZ (ÖNEMSİZ) OLDUĞU GİBİ BIRAKABİLİRSİNİZ
if __name__ == '__main__':
    app.run()