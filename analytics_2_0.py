import mysql.connector
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib


def pull_data():
    utc_year = datetime.utcnow().strftime("%Y")  # Get year in UTC Time Zone
    utc_month = datetime.utcnow().strftime("%m")  # Get month in UTC Time Zone
    utc_day = datetime.utcnow().strftime("%d")  # Get day in UTC Time Zone
    db_access = mysql.connector.connect(user='salk',
                                        password='enGage', host='138.68.246.61',
                                        database='salk')  # Connect to database
    dbcursor = db_access.cursor()  # Create SQL cursor
    # dbcursor.execute("SELECT * from temporal_trails WHERE timestamp BETWEEN "
    #                  "'" + utc_year + "-" + utc_month + "-" + str(int(utc_day)-1) +
    #                  " 08:00:00' AND CURRENT_TIMESTAMP")                         # Query for all of today's data
    dbcursor.execute("SELECT * from temporal_trails WHERE timestamp BETWEEN \'2017-10-05 14:00:00\' AND \'2017-11-07 08:00:00\'")
    trials_data = dbcursor.fetchall()  # Fetch today's trial data

    # dbCursor.execute("SELECT * from temporal_session WHERE timestamp BETWEEN '" +
    #                  utc_year + "-" + utc_month + "-" + str(int(utc_day)-1) +
    #                  " 08:00:00' AND CURRENT_TIMESTAMP")                         # Query for all of today's data
    dbcursor.execute("SELECT * from temporal_session WHERE timestamp BETWEEN \'2017-10-05 14:00:00\' AND \'2017-11-07 08:00:00\'")
    sessions_data = dbcursor.fetchall()
    dbcursor.close()
    db_access.close()
    return sessions_data, trials_data


def extract_data(sessions_data, trials_data):

    #################################
    # EXTRACT SESSIONS NAMES TO SET #
    #################################
    i = len(trials_data)
    data_sessions = set()
    for x in range(0, i):
        data_sessions.add(trials_data[x][2])
    daily_sessions = sorted(list(data_sessions))
    num = len(daily_sessions)

    #######################################
    # REFORMAT SESSION NAMES TO MOUSE IDS #
    #######################################
    mouse_ids = []
    for x in range(0, len(sessions_data)):
        session = sessions_data[x][0]
        for y in range(0, num):
            if session == daily_sessions[y]:
                a = str(sessions_data[x][1])
                if a != '0':
                    mouse_ids.append(a[5:7] + " - Mouse " + a[7])
                else:
                    mouse_ids.append(a)
    ##########################
    # INIT TRIAL DATA ARRAYS #
    ##########################
    t_tot = [0] * num
    t_temp = [0] * num
    t_nt = [0] * num
    l_incor = [0] * num
    l_cor = [0] * num
    l_none = [0] * num
    l_incor_t = [0] * num
    l_cor_t = [0] * num
    l_none_t = [0] * num
    l_incor_nt = [0] * num
    l_cor_nt = [0] * num
    l_none_nt = [0] * num

    ##############################
    # POPULATE TRIAL DATA ARRAYS #
    ##############################
    for x in range(0, len(trials_data)):
        if trials_data[x][8] == 0 and trials_data[x][9] != 0:
            for y in range(0, num):
                if trials_data[x][2] == daily_sessions[y]:
                    l_cor[y] = l_cor[y] + 1
                    t_tot[y] = t_tot[y] + 1
                    if "C8 E9 G8 C9" in str(trials_data[x][5]):
                        t_temp[y] = t_temp[y] + 1
                        l_cor_t[y] = l_cor_t[y] + 1
                    else:
                        t_nt[y] = t_nt[y] + 1
                        l_cor_nt[y] = l_cor_nt[y] + 1
        if trials_data[x][8] == 1:
            for y in range(0, num):
                if trials_data[x][2] == daily_sessions[y]:
                    l_incor[y] = l_incor[y] + 1
                    t_tot[y] = t_tot[y] + 1
                    if "C8 E9 G8 C9" in str(trials_data[x][5]):
                        t_temp[y] = t_temp[y] + 1
                        l_incor_t[y] = l_incor_t[y] + 1
                    else:
                        t_nt[y] = t_nt[y] + 1
                        l_incor_nt[y] = l_incor_nt[y] + 1
        if trials_data[x][9] == 0:
            for y in range(0, num):
                if trials_data[x][2] == daily_sessions[y]:
                    l_none[y] = l_none[y] + 1
                    t_tot[y] = t_tot[y] + 1
                    if "C8 E9 G8 C9" in str(trials_data[x][5]):
                        t_temp[y] = t_temp[y] + 1
                        l_none_t[y] = l_none_t[y] + 1
                    else:
                        t_nt[y] = t_nt[y] + 1
                        l_none_nt[y] = l_none_nt[y] + 1
    to_delete = set()
    for i in range(0, num):
         if t_tot[i] <= 100 or l_cor == 0:
             to_delete.add(i)

    to_delete = list(to_delete)

    for j in range(0, len(to_delete)):
         del t_tot[to_delete[j] - j]
         del t_temp[to_delete[j] - j]
         del t_nt[to_delete[j] - j]
         del l_incor[to_delete[j] - j]
         del l_cor[to_delete[j] - j]
         del l_none[to_delete[j] - j]
         del l_incor_t[to_delete[j] - j]
         del l_cor_t[to_delete[j] - j]
         del l_none_t[to_delete[j] - j]
         del l_incor_nt[to_delete[j] - j]
         del l_cor_nt[to_delete[j] - j]
         del l_none_nt[to_delete[j] - j]
         del mouse_ids[to_delete[j] - j]

    t = [t_tot, l_cor, l_incor, l_none]
    temp = [t_temp, l_cor_t, l_incor_t, l_none_t]
    nt = [t_nt, l_cor_nt, l_incor_nt, l_none_nt]

    return t, temp, nt, mouse_ids


def format_data(correct, incorrect, none, total, mouse_ids):
    plot_data = {}

    for a in range(0, len(mouse_ids)):
        if total[a] - none[a] != 0:
            plot_data[str(mouse_ids[a])] = [100 * float(correct[a]) / (total[a] - none[a]),
                                            100 * float(incorrect[a]) / (total[a] - none[a])]
        else:
            plot_data[str(mouse_ids[a])] = [0, 0]

    plot_data_percent = pd.DataFrame(data=plot_data)

    for a in range(0, len(mouse_ids)):
        plot_data[str(mouse_ids[a])] = [float(correct[a]),
                                        float(incorrect[a]),
                                        float(none[a])]

    plot_data_nominal = pd.DataFrame(data=plot_data)

    return [plot_data_percent, plot_data_nominal]


def create_stacked_graph(panda_plot_data, plot_title):
    panda_plot_data_tp = panda_plot_data.transpose()
    panda_plot_data_tp.columns = ['Correct', 'Incorrect']

    ax = panda_plot_data_tp.plot.barh(stacked=True, figsize = (8,4.5), title = plot_title, legend=False)
    plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
    x_axis = ax.axes.get_xaxis()
    x_axis.set_visible(False)
    columns = list(panda_plot_data)
    for b in range(0, len(panda_plot_data_tp.index)):
        l = panda_plot_data_tp.index
        percent_correct = panda_plot_data[str(l[b])][0]
        percent_incorrect = panda_plot_data[str(l[b])][1]
        #percent_no_lick = panda_plot_data[str(l[b])][2]
        for c in range(0, len(panda_plot_data_tp.index)):
            if str(l[b]) == str(columns[c]):
                ax.text(percent_correct / 2 - 3, c, str(int(percent_correct * 100) / 100.00) + "%", fontsize=10)
                ax.text(percent_correct + percent_incorrect / 2 - 3, c,
                        str((int(percent_incorrect * 100) / 100.00)) + "%", fontsize=10)
                #ax.text(percent_correct + percent_incorrect + percent_no_lick / 2 - 3, c,
                #        str((int(percent_no_lick * 100) / 100.00)) + "%", fontsize=10)
    plt.savefig(plot_title + ".png", bbox_inches='tight', dpi=100)


def format_html_table(table_data):

    ################################################################
    # ADD COLUMN TITLES TO TRASNPOSE AND CONVER ALL MEMBERS TO STR #
    ################################################################
    for i in range(0,3):
        table_data[i] = table_data[i].transpose()
        table_data[i].columns = ['Correct', 'Incorrect', 'No Lick']

    for x in range(0, len(table_data)):
        cursor = table_data[x]
        cursor = cursor.round(2)
        cursor = cursor.applymap(int)
        cursor = cursor.applymap(str)
        table_data[x] = cursor

    table1 = table_data[0]
    table2 = table_data[1]
    table3 = table_data[2]

    ###########################
    # GENERATE HTML FOR TABLE #
    ###########################
    now = datetime.now()

    data = "<table style=\"float: center; width:75%\" border=\"1\" class=\"dataframe\" cellpadding=\"5\" CELLSPACING=\"3\">\n" \
            "  <thead>\n" \
            "    <TH COLSPAN=9>" + now.strftime("%Y-%m-%d") + " Trials Update</TH>\n" \
            "    <tr style=\"text-align: right;\">\n" \
            "      <th style=\"text-align: center;\">Mouse ID</th>\n" \
            "      <th colspan=\"2\" style=\"text-align: center;\">Total</th>\n" \
            "      <th colspan=\"2\" style=\"text-align: center;\">Correct</th>\n" \
            "      <th colspan=\"2\" style=\"text-align: center;\">Incorrect</th>\n" \
            "      <th colspan=\"2\" style=\"text-align: center;\">No Lick</th>\n" \
            "    </tr>\n" \
            "  </thead>\n" \
            "  <tbody>\n" \

    for x in range(0, len(table1.index)):
        total = int(table1['Correct'][x]) + int(table1['Incorrect'][x]) + int(table1['No Lick'][x])
        no_lick = int(table1['No Lick'][x])

        data = data + \
            "    <tr>\n"\
            "      <td rowspan=\"2\" style=\"text-align: center;\">" + table1.index[x] + "</th>\n" \
            "      <td rowspan=\"2\" colspan=\"2\" style=\"text-align: center;\">" + str(total) + "</th>\n"\
            "      <td rowspan=\"2\" style=\"text-align: center;\">" + table1['Correct'][x] + "</th>\n"\
            "      <td rowspan=\"1\" bgcolor=\"green\" style=\"text-align: center;\">" + table2['Correct'][x] + "</th>\n"\
            "      <td rowspan=\"2\" style=\"text-align: center;\">" + table1['Incorrect'][x] + "</th>\n"\
            "      <td rowspan=\"1\" bgcolor=\"green\" style=\"text-align: center;\">" + table2['Incorrect'][x] + "</th>\n"

        if no_lick/total >= .5:
            data = data + "      <td rowspan=\"2\" bgcolor=\"red\" style=\"text-align: center;\">" + table1['No Lick'][x] + "</th>\n"
        else:
            data = data + "      <td rowspan=\"2\" style=\"text-align: center;\">" + table1['No Lick'][x] + "</th>\n"

        data = data + \
            "      <td rowspan=\"1\" bgcolor=\"green\" style=\"text-align: center;\">" + table2['No Lick'][x] + "</th>\n"\
            "    </tr>\n"\
            "    <tr>\n"\
            "      <td rowspan=\"1\" bgcolor=\"yellow\" style=\"text-align: center;\">" + str(table3['Correct'][x]) + "</th>\n"\
            "      <td rowspan=\"1\" bgcolor=\"yellow\" style=\"text-align: center;\">" + str(table3['Incorrect'][x]) + "</th>\n"\
            "      <td rowspan=\"1\" bgcolor=\"yellow\" style=\"text-align: center;\">" + str(table3['No Lick'][x]) + "</th>\n"
    data = data + \
        "    </tr>\n"\
        "    <tr>\n"\
        "      <td colspan=\"9\" style=\"text-align: center;\"><i>Green = Template, Yellow = Non-Template, Red = More than 50% No Lick</i></th>\n" \
        "    </tr>\n" \
        "  <tbody>\n"\
        "</table>"

    return data


def send_email(body, table, image1, image2, image3, strfrom, strto):
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = 'Test of Different visuals'
    msgRoot['From'] = strfrom
    msgRoot['To'] = strto
    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)

    print(str(table))
    msgText = MIMEText(
        '<br>' + body + '<br><br><br><br><center>' + table +
        '<br><img src="cid:image1"><br><br><img src="cid:image2">'
        '<img src="cid:image3"><br>', 'html')
    msgAlternative.attach(msgText)

    fp = open(image1, 'rb')
    msgImage = MIMEImage(fp.read())
    msgImage.add_header('Content-ID', '<image1>')
    msgRoot.attach(msgImage)
    fp = open(image2, 'rb')
    msgImage = MIMEImage(fp.read())
    msgImage.add_header('Content-ID', '<image2>')
    msgRoot.attach(msgImage)
    fp = open(image3, 'rb')
    msgImage = MIMEImage(fp.read())
    msgImage.add_header('Content-ID', '<image3>')
    msgRoot.attach(msgImage)
    fp.close()

    smtp = smtplib.SMTP('smtp.gmail.com:587')
    smtp.ehlo()
    smtp.starttls()
    smtp.login('ozhanaf@gmail.com', 'Theguy1993')
    smtp.sendmail(strfrom, strto, msgRoot.as_string())
    smtp.quit()


[today_session_sql, today_trial_sql] = pull_data()

[all_trials, template_trials, nontemplate_trials, IDs] = extract_data(today_session_sql, today_trial_sql)

all_trials_formatted            = format_data(all_trials[1], all_trials[2], all_trials[3], all_trials[0], IDs)
template_trials_formatted       = format_data(template_trials[1], template_trials[2], template_trials[3], template_trials[0], IDs)
nontemplate_trials_formatted    = format_data(nontemplate_trials[1], nontemplate_trials[2], nontemplate_trials[3], nontemplate_trials[0], IDs)

table = format_html_table([all_trials_formatted[1], template_trials_formatted[1] , nontemplate_trials_formatted[1]])

graphStr1 = 'All Trials'
create_stacked_graph(all_trials_formatted[0], graphStr1)
graphStr2 = 'Template Trial'
create_stacked_graph(template_trials_formatted[0], graphStr2)
graphStr3 = 'Non-Template Trials'
create_stacked_graph(nontemplate_trials_formatted[0], graphStr3)


toStr = 'ozhanaf@gmail.com'
fromStr = 'ozhanaf@gmail.com'

body = 'yo wassup boiiiiiiiiiiiii'

send_email(body, table, graphStr1 + ".png", graphStr2 + ".png", graphStr3 + ".png", fromStr, toStr)



