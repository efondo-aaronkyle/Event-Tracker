from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

DATABASE = "event_tracker.db"