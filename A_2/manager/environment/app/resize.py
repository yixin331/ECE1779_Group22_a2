from flask import render_template,redirect, url_for, request, g
from app import webapp,config
import requests
import boto3


@webapp.route('/resize_pool', methods=['GET','POST'])
def resize_pool(type='all',result=None):

    ec2 = boto3.resource('ec2')
    instances = ec2.instances.all()
    size=0
    for i in instances:
        size = size + 1
    size=size-1
    return render_template("resize/resize_pool.html",title="Resize Pool",size=size,type=type,result=result)

@webapp.route('/shrink_pool', methods=['GET','POST'])
def shrink_pool():
    size=1#requests.post(url='http://localhost:5003/getSize').json()
    #size=size['value']
    return resize_pool(type='manu',result='manual mode')

@webapp.route('/shrink_pool', methods=['GET','POST'])
def expand_pool():
    size=1#requests.post(url='http://localhost:5003/getSize').json()
    #size=size['value']
    return resize_pool(type='manu',result='manual mode')


@webapp.route('/resize_manu', methods=['GET', 'POST'])
def resize_manu():
    return resize_pool(type='manu')


@webapp.route('/resize_auto', methods=['GET', 'POST'])
def resize_auto():
    return resize_pool(type='auto')


@webapp.route('/auto_mode', methods=['GET', 'POST'])
def auto_mode():
    return resize_pool(type='auto',result='Auto mode')