from flask import render_template,redirect, url_for, request, g
from app import webapp,config
import requests
import boto3


@webapp.route('/clear_memcache', methods=['GET','POST'])
def clear_memcache():
    return render_template("clear/clear_memcache.html",title="Clear Pool",result=None)


@webapp.route('/clear', methods=['GET','POST'])
def clear():
    non_mem=['i-02eefcf05aeb184f8']
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.all()
    print('checkkkkpoint')
    for i in instances:
        print(i.id)
    result='cleared'
    return render_template("clear/clear_memcache.html",title="Clear Pool",result=result)
