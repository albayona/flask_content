#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# File name: user_model.py
# Author: Andy Ortiz
# Date created: 11/15/2020
# Date last modified: 11/15/2020
# Python Version: 3.9.0
# =============================================================================
# =============================================================================
# Imports
# =============================================================================

from flask_restful import reqparse


class UserParser:
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True, help="Must have a username.")
    parser.add_argument('password', type=str, required=True, help="Must have a password.")
    parser.add_argument('email', type=str, required=True, help="Must have an email.")
    parser.add_argument('first_name', type=str, required=True, help="Must have a first name.")
    parser.add_argument('last_name', type=str, required=True, help="Must have a last name.")
    parser.add_argument('description', type=str, required=False)
    parser.add_argument('picture', type=str, required=False)
    parser.add_argument('code', type=int, required=True, help="Must have a code.")
    parser.add_argument('role', type=str, required=True, help="Must have a role.")


