#!/bin/bash
echo "Starting your Lenovo Notification Telegram app with Gunicorn..."
gunicorn main:app --bind 0.0.0.0:$PORT
echo "Application has stopped."
