from flask import render_template,redirect, url_for, request, g
from app import webapp,config
import requests
import boto3


@webapp.route('/delete_all', methods=['GET','POST'])
def delete_all():
    return render_template("delete_all/delete_all.html",title="Clear Pool",result=None)


@webapp.route('/delete', methods=['GET','POST'])
def delete():

    result='cleared'
    return render_template("delete_all/delete_all.html",title="Clear Pool",result=result)
