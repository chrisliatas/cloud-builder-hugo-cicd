#!/bin/bash

# Based on: https://github.com/GoogleCloudPlatform/cloud-builders-community/blob/master/firebase/firebase.bash
# run a firebase command with token 'FIREBASE_TOKEN'
firebase "$@" --token $FIREBASE_TOKEN
