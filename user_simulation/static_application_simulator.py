# simulate the behaviour in an application where the scenarios are prefixed and the user can only go through certain
# conditions to accomplish a goal
# for example, a user cannot book without first checking availability or cannot checking parking without booking tickets
# in some sense these are all pre-defined by the application and does not provide flexibilit

# Replace "localhost" with ip address of the corresponding hosts

# based on the FIFA 98 world cup trace


import requests
import asyncio
from concurrent.futures import ThreadPoolExecutor
from timeit import default_timer
import json
from datetime import datetime
from SQL_Util import SQLUtils
import math
import random
import time
import json
from Goal_Parser import Goal_Parser

parse_obj = Goal_Parser()


json_data = {}


json_data["venue_number"] = 1
json_data["username"] = "username"
trace_type = "wc_trace"


# FIFA 98 World cup trace, each value in the list indicates the number of requests per second 

wc_trace_list = [10, 13, 12, 13, 11, 12, 13, 13, 12, 12, 12, 12, 12, 12, 13, 13, 14, 13, 12, 12, 12, 12, 11, 12, 11, 13, 12, 12, 13, 13, 12, 11, 12, 13, 12, 12, 11, 12, 12, 12, 11, 12, 11, 12, 11, 12, 12, 12, 11, 11, 11, 11, 11, 11, 10, 10, 10, 11, 11, 10, 11, 12, 10, 11, 11, 11, 11, 11, 11, 12, 11, 10, 9, 10, 11, 10, 10, 10, 10, 10, 10, 11, 10, 11, 9, 10, 9, 10, 11, 12, 11, 10, 11, 11, 10, 10, 11, 11, 12, 12, 11, 11, 10, 11, 11, 10, 11, 10, 12, 10, 12, 10, 11, 10, 11, 11, 11, 10, 10, 11, 10, 10, 11, 11, 12, 11, 11, 11, 11, 10, 12, 11, 11, 10, 11, 11, 11, 11, 12, 11, 11, 12, 10, 11, 10, 11, 12, 11, 10, 11, 11, 11, 10, 11, 11, 11, 10, 10, 10, 11, 11, 10, 11, 10, 10, 10, 10, 11, 10, 11, 11, 11, 10, 11, 11, 10, 10, 10, 11, 10, 10, 10, 9, 10, 10, 10, 12, 10, 11, 10, 10, 10, 10, 10, 11, 11, 10, 10, 11, 10, 10, 10, 10, 8, 10, 10, 9, 9, 9, 10, 10, 11, 10, 10, 10, 10, 10, 9, 10, 9, 9, 9, 9, 10, 10, 10, 11, 10, 10, 10, 11, 10, 9, 11, 9, 10, 10, 9, 10, 10, 11, 9, 9, 10, 9, 10, 10, 10, 9, 10, 10, 9, 9, 11, 10, 10, 9, 11, 9, 9, 10, 9, 9, 9, 11, 10, 10, 10, 11, 10, 9, 9, 11, 9, 10, 10, 11, 10, 10, 11, 10, 9, 10, 10, 9, 10, 9, 10, 10, 9, 10, 10, 10, 10, 9, 9, 9, 11, 10, 11, 10, 11, 10, 9, 9, 9, 9, 9, 9, 10, 9, 9, 9, 10, 9, 9, 9, 9, 10, 9, 10, 9, 9, 9, 10, 10, 8, 9, 9, 9, 9, 10, 9, 10, 8, 9, 9, 9, 9, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 10, 9, 10, 9, 9, 9, 9, 10, 9, 9, 9, 10, 9, 10, 9, 10, 11, 10, 11, 10, 10, 11, 11, 10, 11, 10, 10, 9, 10, 9, 10, 10, 10, 9, 10, 10, 9, 9, 9, 10, 9, 10, 10, 10, 10, 10, 10, 10, 10, 11, 11, 10, 9, 10, 9, 9, 9, 10, 9, 8, 9, 9, 9, 10, 9, 10, 10, 10, 9, 9, 10, 9, 9, 8, 8, 9, 9, 9, 9, 9, 10, 9, 9, 9, 8, 10, 9, 10, 9, 9, 10, 9, 9, 10, 9, 10, 9, 10, 9, 9, 9, 9, 8, 8, 9, 9, 9, 10, 9, 9, 9, 9, 9, 8, 9, 9, 9, 8, 10, 9, 10, 9, 9, 10, 9, 9, 10, 9, 10, 10, 9, 9, 10, 10, 10, 9, 10, 9, 11, 10, 11, 10, 10, 9, 9, 10, 10, 10, 10, 10, 10, 11, 10, 10, 10, 10, 10, 9, 9, 9, 9, 10, 10, 9, 10, 9, 10, 9, 10, 9, 10, 10, 11, 10, 10, 10, 9, 10, 9, 8, 9, 10, 10, 10, 10, 10, 9, 11, 10, 10, 10, 11, 10, 9, 9, 10, 10, 10, 9, 10, 9, 9, 9, 9, 10, 9, 9, 9, 10, 9, 10, 9, 10, 10, 10, 10, 11, 10, 10, 11, 10, 10, 10, 10, 11, 9, 10, 10, 10, 9, 9, 10, 10, 9, 11, 10, 10, 10, 10, 10, 10, 10, 9, 11, 9, 9, 10, 10, 10, 10, 10, 9, 10, 10, 10, 10, 10, 10, 10, 10, 9, 9, 8, 9, 10, 9, 9, 9, 9, 10, 10, 9, 9, 10, 9, 10, 11, 9, 10, 10, 9, 10, 9, 9, 9, 9, 10, 10, 9, 8, 9, 9, 9, 9, 9, 10, 9, 10, 9, 10, 9, 10, 11, 10, 10, 10, 8, 9, 9, 9, 9, 9, 10, 10, 10, 10, 9, 9, 10, 9, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 9, 10, 10, 9, 9, 9, 9, 10, 9, 10, 9, 9, 9, 10, 10, 9, 9, 10, 11, 10, 10, 10, 10, 10, 10, 10, 10, 9, 10, 9, 9, 10, 9, 10, 9, 9, 9, 10, 9, 10, 9, 9, 10, 9, 10, 9, 10, 9, 9, 8, 9, 9, 9, 9, 9, 9, 10, 10, 9, 10, 9, 9, 9, 10, 10, 9, 10, 9, 9, 9, 9, 10, 9, 10, 10, 11, 10, 10, 9, 9, 10, 9, 10, 9, 10, 10, 10, 10, 10, 11, 9, 10, 8, 10, 9, 9, 8, 9, 10, 9, 10, 10, 9, 10, 9, 10, 10, 10, 10, 9, 9, 9, 10, 9, 9, 9, 9, 9, 8, 8, 9, 9, 9, 8, 9, 9, 9, 10, 9, 9, 11, 10, 10, 9, 10, 9, 9, 10, 9, 9, 9, 10, 9, 8, 9, 9, 10, 9, 10, 9, 8, 9, 8, 9, 9, 9, 9, 9, 9, 10, 9, 10, 9, 10, 9, 10, 9, 10, 9, 9, 9, 9, 9, 8, 9, 9, 9, 9, 8, 9, 9, 9, 9, 10, 9, 10, 10, 9, 9, 9, 9, 10, 9, 10, 9, 10, 9, 9, 8, 9, 9, 9, 9, 9, 9, 9, 8, 9, 9, 10, 9, 10, 9, 9, 9, 9, 9, 10, 9, 8, 10, 9, 8, 9, 8, 8, 9, 8, 8, 9, 8, 8, 9, 9, 8, 8, 9, 8, 8, 9, 8, 8, 9, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 8, 9, 8, 8, 9, 8, 8, 9, 8, 9, 9, 8, 9, 8, 9, 8, 9, 8, 9, 9, 9, 9, 9, 9, 8, 9, 9, 9, 10, 9, 8, 9, 9, 8, 9, 9, 9, 8, 9, 8, 9, 9, 8, 8, 9, 9, 8, 8, 8, 9, 8, 9, 9, 9, 8, 8, 10, 9, 8, 8, 8, 9, 7, 9, 8, 8, 8, 8, 8, 8, 9, 9, 9, 8, 8, 8, 8, 8, 7, 8, 8, 8, 7, 8, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 8, 8, 8, 9, 8, 7, 8, 7, 8, 7, 8, 7, 9, 8, 8, 8, 8, 9, 8, 8, 7, 8, 8, 9, 8, 9, 8, 9, 9, 9, 8, 9, 8, 7, 8, 8, 7, 9, 7, 7, 8, 7, 9, 8, 8, 8, 8, 8, 9, 8, 8, 7, 8, 8, 7, 8, 7, 8, 8, 7, 8, 7, 7, 8, 9, 8, 7, 8, 7, 7, 8, 8, 7, 8, 7, 8, 7, 8, 8, 8, 8, 7, 8, 7, 7, 8, 7, 8, 8, 8, 8, 7, 8, 8, 8, 7, 8, 7, 8, 7, 8, 8, 8, 8, 7, 8, 7, 8, 8, 9, 8, 8, 9, 8, 8, 9, 9, 8, 8, 9, 8, 7, 9, 7, 8, 8, 7, 7, 8, 7, 7, 8, 8, 7, 8, 7, 8, 8, 9, 7, 8, 7, 8, 7, 8, 7, 8, 7, 8, 7, 8, 8, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 7, 7, 8, 7, 7, 8, 8, 8, 8, 7, 8, 7, 7, 7, 7, 7, 8, 7, 8, 8, 7, 8, 8, 7, 8, 7, 8, 7, 8, 8, 7, 9, 7, 8, 8, 8, 8, 7, 7, 8, 7, 7, 7, 8, 8, 8, 7, 8, 8, 8, 8, 8, 8, 8, 8, 7, 7, 8, 7, 8, 7, 7, 8, 8, 7, 7, 8, 7, 8, 7, 7, 8, 7, 7, 6, 7, 7, 7, 7, 6, 7, 7, 7, 7, 6, 7, 7, 7, 8, 7, 7, 6, 7, 8, 6, 7, 7, 8, 7, 7, 8, 6, 8, 7, 6, 7, 8, 7, 7, 8, 6, 7, 7, 7, 7, 6, 7, 7, 7, 6, 7, 7, 7, 7, 7, 7, 7, 7, 8, 7, 8, 7, 7, 8, 7, 7, 7, 7, 8, 7, 8, 7, 8, 8, 7, 8, 7, 9, 8, 8, 8, 8, 8, 7, 8, 8, 7, 8, 6, 8, 7, 9, 7, 8, 8, 7, 8, 7, 8, 7, 6, 8, 7, 7, 8, 7, 7, 7, 8, 8, 8, 7, 8, 8, 8, 8, 7, 8, 8, 8, 7, 8, 8, 8, 7, 7, 8, 7, 7, 8, 7, 7, 7, 8, 8, 7, 9, 8, 8, 8, 7, 8, 8, 8, 8, 7, 8, 8, 9, 8, 8, 8, 7, 9, 7, 8, 9, 7, 8, 8, 9, 8, 9, 8, 8, 9, 8, 9, 8, 9, 9, 9, 8, 8, 9, 8, 9, 8, 8, 8, 9, 8, 8, 8, 8, 7, 8, 8, 8, 8, 8, 9, 7, 8, 8, 9, 8, 8, 8, 8, 8, 8, 8, 7, 8, 9, 8, 8, 8, 8, 8, 8, 8, 9, 8, 8, 9, 9, 8, 7, 7, 9, 8, 8, 8, 8, 8, 8, 9, 8, 8, 9, 8, 8, 8, 8, 8, 8, 8, 8, 8, 7, 8, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 7, 8, 7, 7, 8, 8, 9, 8, 8, 8, 8, 7, 8, 8, 8, 7, 7, 7, 8, 7, 8, 7, 8, 7, 7, 8, 9, 7, 8, 8, 8, 8, 8, 7, 7, 8, 8, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 7, 8, 6, 8, 7, 8, 8, 8, 7, 7, 8, 7, 7, 7, 7, 7, 8, 7, 8, 7, 8, 8, 7, 7, 7, 7, 7, 7, 8, 8, 7, 6, 7, 7, 7, 7, 7, 7, 6, 8, 7, 7, 7, 7, 8, 8, 7, 7, 6, 7, 6, 7, 7, 7, 7, 7, 8, 6, 8, 7, 6, 7, 8, 7, 7, 9, 8, 7, 7, 8, 8, 7, 8, 7, 7, 7, 7, 7, 8, 7, 6, 8, 6, 7, 6, 7, 7, 7, 7, 6, 7, 7, 7, 7, 7, 6, 7, 7, 7, 6, 7, 8, 7, 7, 7, 7, 6, 7, 7, 7, 7, 6, 6, 7, 6, 7, 7, 6, 6, 7, 7, 8, 7, 7, 7, 7, 8, 6, 8, 6, 7, 7, 7, 7, 6, 7, 7, 7, 8, 7, 6, 7, 7, 7, 7, 6, 7, 7, 6, 6, 7, 6, 7, 7, 7, 7, 7, 7, 7, 7, 6, 6, 7, 7, 6, 7, 7, 7, 7, 7, 8, 7, 6, 7, 7, 7, 6, 7, 6, 7, 6, 6, 7, 7, 7, 7, 7, 7, 7, 6, 7, 6, 7, 6, 7, 6, 6, 7, 7, 7, 7, 8, 7, 6, 7, 8, 6, 6, 7, 7, 7, 6, 7, 7, 7, 6, 6, 7, 7, 6, 7, 7, 6, 6, 7, 6, 7, 8, 7, 7, 7, 7, 7, 7, 7, 6, 7, 7, 7, 7, 7, 6, 7, 6, 6, 7, 6, 7, 6, 7, 7, 7, 6, 7, 6, 7, 6, 6, 7, 6, 6, 7, 6, 6, 7, 6, 6, 6, 8, 7, 6, 6, 7, 7, 7, 6, 7, 6, 7, 6, 7, 7, 7, 7, 7, 6, 7, 7, 6, 6, 7, 7, 7, 6, 7, 7, 6, 6, 7, 6, 6, 7, 7, 7, 8, 7, 8, 7, 7, 7, 6, 7, 7, 7, 7, 7, 8, 7, 7, 7, 7, 6, 7, 7, 7, 7, 7, 6, 7, 7, 7, 8, 6, 7, 7, 6, 7, 7, 6, 7, 7, 6, 7, 6, 7, 7, 6, 8, 6, 7, 6, 6, 7, 6, 7, 6, 7, 6, 6, 7, 7, 6, 6, 7, 7, 7, 7, 6, 7, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 6, 7, 8, 7, 7, 7, 7, 6, 7, 6, 7, 7, 6, 6, 7, 7, 6, 6, 7, 7, 7, 8, 7, 8, 7, 8, 6, 7, 8, 7, 8, 7, 8, 8, 8, 8, 7, 7, 8, 7, 8, 8, 7, 7, 7, 8, 7, 7, 6, 7, 6, 7, 6, 7, 6, 7, 7, 7, 7, 7, 6, 8, 6, 8, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 8, 7, 7, 7, 7, 7, 7, 6, 7, 7, 8, 7, 7, 7, 7, 8, 7, 7, 8, 8, 7, 8, 7, 6, 7, 7, 6, 7, 8, 7, 7, 8, 7, 7, 8, 6, 7, 7, 7, 8, 7, 6, 8, 7, 7, 7, 7, 7, 7, 7, 6, 7, 8, 6, 8, 7, 7, 7, 6, 8, 7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 7, 8, 7, 8, 7, 8, 8, 7, 8, 7, 8, 8, 8, 8, 7, 7, 8, 8, 7, 8, 8, 8, 8, 7, 7, 7, 7, 8, 7, 7, 8, 8, 7, 8, 9, 7, 8, 8, 8, 7, 9, 7, 8, 8, 8, 8, 8, 8, 9, 8, 8, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 7, 9, 8, 7, 8, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 7, 8, 7, 8, 8, 8, 8, 7, 8, 8, 7, 8, 8, 9, 8, 8, 9, 8, 8, 8, 7, 8, 7, 8, 8, 8, 7, 8, 8, 8, 8, 7, 8, 8, 8, 8, 9, 8, 8, 9, 8, 8, 9, 8, 9, 9, 8, 8, 8, 9, 9, 8, 9, 8, 9, 8, 8, 8, 9, 7, 8, 8, 7, 7, 8, 8, 8, 8, 9, 9, 8, 8, 8, 8, 8, 8, 8, 8, 9, 8, 8, 8, 8, 9, 8, 7, 7, 8, 8, 8, 9, 9, 8, 7, 9, 8, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 8, 8, 9, 8, 9, 9, 8, 8, 9, 8, 9, 9, 8, 8, 8, 8, 7, 9, 7, 8, 8, 8, 7, 7, 8, 7, 8, 8, 8, 8, 9, 8, 9, 9, 9, 8, 8, 7, 8, 8, 8, 8, 9, 8, 8, 8, 8, 7, 8, 7, 8, 9, 8, 7, 8, 8, 7, 8, 9, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 8, 8, 9, 8, 8, 9, 9, 9, 9, 8, 9, 8, 9, 8, 9, 8, 8, 9, 8, 9, 8, 8, 8, 7, 8, 8, 8, 9, 8, 8, 8, 8, 9, 9, 8, 8, 8, 9, 9, 8, 9, 8, 8, 9, 8, 9, 8, 8, 8, 8, 7, 8, 9, 8, 8, 9, 9, 8, 9, 9, 9, 8, 9, 8, 8, 8, 8, 8, 8, 9, 7, 8, 7, 8, 8, 8, 8, 8, 8, 9, 9, 7, 8, 9, 8, 8, 9, 8, 8, 8, 8, 9, 8, 8, 9, 8, 8, 8, 9, 8, 8, 8, 8, 8, 8, 8, 7, 8, 8, 9, 8, 9, 8, 8, 8, 8, 8, 8, 9, 8, 9, 9, 8, 9, 8, 9, 8, 9, 7, 7, 9, 7, 8, 8, 8, 8, 8, 8, 9, 9, 8, 8, 8, 9, 8, 8, 9, 8, 8, 8, 8, 8, 8, 7, 8, 9, 8, 8, 8, 8, 8, 9, 7, 8, 8, 8, 9, 8, 8, 8, 8, 8, 9, 8, 9, 8, 8, 8, 9, 8, 8, 9, 8, 8, 8, 8, 8, 9, 8, 9, 10, 8, 9, 8, 9, 8, 9, 9, 9, 8, 8, 9, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 10, 9, 8, 9, 9, 8, 9, 9, 9, 9, 8, 9, 8, 9, 9, 8, 7, 8, 8, 8, 7, 9, 8, 8, 8, 9, 9, 8, 9, 9, 8, 9, 9, 8, 9, 9, 9, 8, 8, 7, 8, 9, 8, 8, 9, 8, 9, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 8, 8, 9, 9, 8, 8, 8, 8, 9, 9, 9, 8, 8, 9, 9, 7, 9, 8, 8, 8, 8, 8, 9, 8, 9, 9, 9, 8, 9, 8, 8, 9, 9, 8, 9, 9, 9, 8, 8, 8, 9, 8, 8, 8, 8, 9, 8, 9, 9, 9, 9, 9, 9, 8, 9, 8, 8, 9, 8, 9, 8, 8, 9, 8, 8, 9, 9, 8, 8, 8, 9, 8, 9, 9, 8, 9, 9, 9, 8, 9, 9, 8, 8, 9, 8, 8, 9, 8, 8, 8, 8, 9, 8, 8, 9, 8, 9, 8, 9, 9, 10, 9, 9, 9, 9, 9, 9, 9, 8, 9, 8, 9, 9, 8, 9, 8, 9, 8, 8, 8, 9, 9, 9, 8, 8, 8, 8, 9, 8, 8, 8, 8, 8, 7, 9, 8, 8, 9, 8, 9, 8, 9, 8, 8, 8, 8, 9, 8, 8, 9, 8, 9, 8, 9, 8, 9, 9, 8, 9, 8, 8, 8, 8, 8, 7, 8, 9, 8, 9, 8, 9, 8, 9, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 7, 8, 7, 8, 8, 8, 9, 8, 7, 8, 8, 8, 8, 8, 7, 7, 7, 8, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 9, 8, 8, 8, 9, 8, 9, 8, 9, 8, 8, 8, 8, 8, 9, 8, 8, 8, 8, 7, 8, 9, 8, 7, 9, 8, 8, 8, 8, 9, 8, 8, 8, 8, 8, 8, 8, 8, 8, 7, 9, 8, 9, 8, 9, 8, 9, 8, 8, 8, 8, 8, 8, 8, 7, 8, 9, 8, 8, 9, 8, 9, 8, 8, 9, 9, 9, 8, 9, 9, 8, 8, 8, 7, 9, 8, 9, 8, 7, 9, 8, 7, 8, 8, 7, 8, 8, 8, 8, 8, 8, 7, 8, 8, 7, 9, 8, 8, 8, 9, 8, 9, 7, 8, 8, 7, 7, 7, 8, 8, 8, 8, 7, 7, 8, 9, 8, 8, 8, 9, 8, 8, 8, 9, 8, 7, 9, 7, 9, 8, 9, 8, 9, 9, 8, 8, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 8, 9, 8, 9, 8, 8, 7, 8, 7, 8, 7, 8, 7, 8, 8, 8, 9, 8, 8, 9, 8, 7, 8, 7, 8, 9, 8, 7, 8, 8, 8, 8, 8, 9, 8, 8, 8, 8, 9, 8, 7, 8, 9, 9, 8, 9, 9, 9, 8, 9, 8, 9, 9, 7, 8, 7, 8, 8, 8, 7, 8, 7, 9, 8, 8, 8, 8, 8, 7, 7, 8, 8, 7, 7, 8, 8, 8, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 8, 8, 8, 9, 8, 9, 8, 8, 7, 8, 7, 8, 7, 9, 8, 7, 8, 9, 8, 8, 8, 9, 8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 8, 7, 9, 9, 8, 8, 8, 8, 8, 9, 8, 8, 8, 9, 8, 8, 8, 7, 8, 7, 9, 8, 8, 9, 9, 17, 17, 17, 16, 17, 18, 16, 17, 17, 16, 16, 16, 15, 15, 16, 16, 16, 17, 16, 16, 16, 16, 15, 16, 17, 16, 15, 16, 15, 16, 16, 15, 16, 16, 17, 16, 16, 15, 16, 16, 16, 14, 15, 15, 14, 15, 16, 15, 15, 15, 17, 17, 16, 17, 16, 17, 17, 16, 17, 16, 17, 16, 15, 17, 16, 16, 17, 16, 17, 18, 17, 17, 17, 16, 17, 18, 15, 16, 15, 17, 16, 17, 18, 16, 17, 16, 17, 17, 16, 17, 16, 17, 15, 15, 15, 15, 16, 17, 16, 16, 16, 16, 16, 16, 16, 18, 17, 16, 16, 16, 16, 17, 16, 17, 16, 16, 17, 17, 17, 17, 16, 16, 17, 17, 16, 16, 17, 17, 18, 17, 16, 17, 18, 18, 19, 18, 19, 17, 19, 16, 18, 15, 16, 16, 16, 16, 16, 18, 15, 15, 15, 15, 16, 14, 15, 16, 16, 17, 17, 16, 17, 16, 16, 16, 16, 16, 17, 18, 16, 16, 16, 16, 16, 15, 15, 16, 17, 16, 16, 17, 16, 18, 16, 16, 18, 16, 15, 17, 17, 18, 17, 18, 18, 18, 17, 16, 17, 17, 17, 17, 16, 17, 16, 18, 16, 18, 18, 18, 17, 17, 18, 18, 17, 17, 16, 15, 18, 17, 16, 16, 16, 17, 19, 18, 18, 18, 19, 20, 20, 19, 18, 18, 18, 18, 19, 20, 19, 19, 19, 18, 19, 18, 18, 19, 20, 18, 20, 18, 19, 18, 18, 20, 20, 18, 19, 18, 18, 17, 20, 18, 18, 17, 18, 17, 18, 18, 17, 17, 16, 17, 17, 17, 17, 19, 18, 17, 19, 18, 17, 18, 17, 18, 17, 18, 18, 18, 18, 18, 18, 18, 18, 19, 21, 18, 19, 20, 19, 18, 18, 18, 19, 17, 17, 18, 18, 17, 17, 18, 16, 19, 17, 18, 17, 17, 18, 18, 18, 18, 18, 18, 18, 17, 18, 20, 19, 20, 20, 19, 21, 18, 19, 18, 18, 18, 19, 19, 18, 20, 19, 19, 18, 19, 18, 19, 19, 19, 19, 18, 18, 18, 19, 18, 18, 18, 18, 17, 17, 18, 17, 18, 17, 17, 18, 18, 19, 18, 18, 18, 19, 17, 17, 16, 16, 18, 17, 17, 16, 18, 18, 17, 15, 16, 17, 18, 18, 18, 19, 18, 19, 18, 20, 20, 19, 18, 19, 19, 19, 18, 19, 18, 17, 17, 17, 19, 20, 19, 19, 20, 20, 20, 19, 21, 20, 19, 20, 19, 20, 19, 19, 18, 19, 18, 19, 20, 19, 22, 21, 21, 21, 19, 19, 20, 18, 18, 20, 20, 21, 20, 20, 22, 21, 21, 21, 20, 20, 20, 20, 21, 22, 20, 19, 19, 20, 21, 19, 21, 21, 21, 22, 21, 22, 21, 22, 21, 22, 22, 21, 20, 20, 18, 20, 19, 20, 20, 21, 19, 20, 18, 21, 21, 21, 19, 20, 19, 19, 20, 19, 19, 19, 19, 19, 19, 20, 21, 19, 19, 19, 19, 18, 19, 19, 19, 17, 19, 18, 20, 19, 19, 20, 20, 19, 20, 19, 20, 19, 19, 19, 19, 19, 19, 19, 20, 19, 19, 21, 21, 21, 19, 19, 18, 19, 21, 21, 20, 19, 19, 21, 20, 19, 22, 20, 22, 21, 21, 21, 21, 20, 21, 21, 22, 21, 21, 21, 20, 21, 20, 21, 20, 21, 21, 20, 20, 21, 21, 20, 21, 21, 21, 21, 23, 23, 21, 23, 22, 23, 21, 22, 21, 21, 21, 21, 22, 23, 23, 23, 23, 22, 21, 21, 23, 23, 22, 20, 22, 20, 22, 21, 20, 22, 22, 23, 22, 23, 25, 25, 24, 24, 22, 22, 23, 22, 20, 21, 21, 21, 21, 20, 19, 21, 22, 21, 23, 23, 24, 24, 23, 21, 22, 22, 22, 24, 23, 21, 22, 22, 21, 22, 24, 23, 22, 23, 23, 22, 22, 24, 22, 24, 23, 24, 23, 23, 25, 25, 23, 22, 24, 24, 22, 23, 24, 24, 24, 22, 24, 25, 23, 22, 24, 25, 26, 26, 23, 25, 25, 25, 24, 24, 25, 24, 23, 24, 25, 23, 24, 22, 24, 24, 23, 24, 23, 24, 22, 25, 23, 23, 23, 22, 22, 24, 23, 23, 24, 22, 23, 25, 23, 26, 25, 25, 24, 23, 25, 26, 25, 25, 25, 26, 28, 26, 24, 23, 23, 25, 24, 24, 23, 24, 24, 25, 22, 23, 24, 25, 24, 24, 25, 24, 25, 24, 25, 25, 25, 25, 25, 25, 24, 24, 24, 23, 22, 23, 23, 23, 22, 25, 25, 24, 25, 24, 25, 23, 24, 24, 25, 24, 24, 24, 24, 24, 24, 24, 25, 26, 27, 27, 26, 25, 28, 25, 26, 27, 27, 27, 27, 27, 26, 27, 26, 26, 26, 26, 26, 25, 24, 25, 26, 27, 27, 26, 27, 25, 26, 26, 26, 25, 24, 27, 28, 28, 25, 26, 26, 26, 25, 25, 27, 26, 26, 28, 27, 28, 27, 27, 27, 25, 27, 26, 27, 25, 26, 28, 27, 26, 27, 28, 27, 29, 25, 28, 28, 27, 26, 28, 26, 27, 26, 26, 26, 27, 24, 25, 24, 28, 28, 28, 30, 31, 28, 27, 29, 31, 28, 28, 26, 28, 29, 26, 26, 28, 28, 30, 27, 27, 26, 28, 28, 25, 25, 29, 27, 27, 27, 28, 26, 29, 28, 27, 28, 27, 29, 27, 27, 27, 27, 27, 28, 27, 26, 25, 25, 24, 26, 26, 26, 26, 26, 26, 27, 27, 27, 25, 26, 26, 26, 25, 25, 27, 27, 27, 26, 27, 25, 27, 28, 28, 27, 28, 26, 27, 25, 26, 26, 27, 27, 29, 29, 26, 27, 27, 27, 27, 27, 27, 25, 27, 27, 28, 26, 26, 26, 27, 24, 24, 26, 26, 27, 27, 26, 28, 25, 26, 27, 26, 29, 28, 29, 28, 27, 27, 30, 27, 29, 29, 28, 28, 28, 29, 28, 28, 29, 29, 28, 28, 27, 27, 27, 24, 24, 26, 25, 26, 25, 26, 26, 26, 26, 25, 27, 27, 26, 26, 27, 29, 27, 26, 26, 26, 27, 27, 27, 29, 27, 28, 27, 28, 28, 27, 26, 26, 25, 26, 25, 26, 27, 25, 27, 24, 27, 26, 27, 27, 27, 26, 26, 28, 28, 26, 26, 26, 27, 27, 26, 28, 27, 25, 26, 25, 28, 27, 27, 27, 29, 27, 27, 29, 28, 29, 27, 25, 27, 28, 28, 26, 27, 30, 28, 29, 29, 28, 28, 29, 29, 30, 29, 32, 29, 28, 28, 26, 29, 27, 28, 27, 30, 32, 28, 28, 31, 28, 28, 29, 27, 27, 30, 28, 30, 30, 29, 28, 30, 31, 31, 29, 27, 28, 27, 26, 27, 26, 26, 26, 25, 26, 30, 34, 34, 32, 32, 31, 31, 29, 29, 30, 30, 30, 31, 30, 28, 28, 31, 31, 28, 29, 29, 31, 30, 30, 29, 28, 29, 28, 28, 29, 28, 28, 29, 30, 29, 27, 30, 30, 30, 30, 29, 31, 31, 30, 29, 30, 29, 30, 29, 31, 29, 30, 29, 29, 31, 28, 28, 29, 28, 29, 28, 27, 27, 30, 28, 30, 29, 28, 27, 28, 29, 28, 27, 28, 29, 30, 29, 28, 28, 28, 31, 30, 32, 31, 33, 31, 30, 30, 30, 31, 30, 29, 32, 32, 32, 30, 32, 32, 31, 31, 30, 31, 32, 31, 30, 30, 31, 29, 32, 32, 35, 33, 30, 30, 30, 32, 30, 32, 31, 31, 31, 29, 30, 29, 29, 31, 29, 29, 33, 31, 30, 30, 32, 31, 32, 31, 30, 29, 29, 28, 30, 31, 31, 29, 30, 32, 31, 31, 29, 30, 32, 31, 30, 31, 30, 32, 32, 31, 33, 32, 31, 33, 31, 32, 31, 31, 31, 31, 32, 33, 30, 31, 30, 29, 32, 29, 31, 29, 31, 32, 30, 30, 29, 29, 31, 31, 28, 29, 30, 28, 29, 28, 29, 29, 30, 29, 30, 30, 32, 31, 31, 30, 32, 31, 30, 33, 31, 32, 30, 32, 35, 33, 32, 32, 31, 31, 30, 29, 30, 33, 34, 35, 35, 32, 34, 31, 31, 30, 35, 35, 33, 33, 34, 36, 34, 36, 36, 36, 36, 35, 34, 34, 34, 32, 33, 35, 32, 32, 30, 33, 33, 33, 32, 31, 31, 30, 31, 30, 34, 33, 35, 35, 34, 34, 33, 35, 34, 34, 36, 36, 34, 35, 35, 37, 34, 35, 35, 35, 33, 34, 34, 35, 36, 35, 35, 33, 36, 35, 35, 35, 31, 34, 33, 33, 33, 34, 34, 33, 34, 32, 32, 35, 36, 34, 34, 33, 34, 33, 34, 32, 33, 36, 36, 35, 36, 35, 39, 36, 36, 37, 34, 35, 36, 37, 37, 39, 39, 39, 40, 39, 41, 39, 40, 41, 40, 40, 40, 42, 43, 44, 41, 44, 43, 43, 42, 43, 42, 43, 43, 46, 46, 45, 45, 47, 50, 48, 47, 48, 47, 47, 50, 50, 48, 47, 50, 50, 49, 50, 47, 50, 50, 50, 51, 53, 51, 49, 49, 50, 52, 55, 52, 53, 51, 52, 51, 50, 52, 50, 51, 52, 54, 55, 53, 54, 54, 49, 53, 54, 57, 55, 55, 56, 57, 60, 58, 57, 54, 57, 55, 56, 56, 55, 56, 57, 55, 53, 54, 56, 57, 59, 59, 58, 61, 58, 55, 55, 57, 58, 58, 56, 57, 56, 58, 58, 54, 59, 57, 56, 57, 60, 55, 57, 56, 57, 55, 56, 55, 56, 54, 56, 57, 60, 58, 60, 58, 60, 61, 57, 56, 59, 58, 59, 59, 59, 59, 57, 59, 58, 58, 55, 55, 59, 59, 62, 61, 61, 58, 56, 58, 55, 57, 60, 60, 60, 61, 62, 57, 58, 60, 61, 62, 66, 63, 61, 60, 62, 63, 60, 60, 61, 60, 58, 59, 57, 61, 62, 61, 61, 59, 61, 59, 61, 61, 61, 59, 63, 61, 59, 59, 60, 59, 61, 59, 60, 62, 61, 63, 59, 62, 65, 62, 65, 64, 66, 65, 64, 60, 59, 61, 60, 62, 61, 61, 63, 67, 64, 66, 63, 63, 61, 65, 65, 64, 68, 66, 61, 63, 64, 63, 60, 65, 66, 64, 63, 69, 66, 66, 65, 61, 58, 63, 64, 62, 63, 63, 62, 60, 61, 64, 61, 61, 62, 60, 61, 65, 62, 61, 63, 57, 61, 60, 58, 56, 55, 55, 56, 56, 59, 59, 57, 57, 60, 62, 60, 59, 59, 60, 57, 58, 58, 57, 57, 55, 54, 55, 59, 60, 61, 59, 56, 58, 55, 55, 56, 57, 57, 54, 58, 55, 56, 54, 56, 57, 56, 56, 55, 55, 55, 56, 58, 57, 58, 58, 59, 59, 58, 58, 56, 57, 55, 57, 57, 56, 57, 57, 56, 59, 59, 60, 59, 60, 58, 56, 59, 58, 58, 57, 57, 61, 60, 60, 56, 56, 56, 60, 58, 59, 59, 59, 59, 61, 58, 57, 61, 62, 58, 56, 58, 61, 58, 57, 58, 58, 58, 60, 61, 58, 59, 60, 61, 59, 59, 59, 59, 59, 60, 59, 60, 60, 60, 59, 61, 63, 61, 62, 63, 59, 64, 65, 64, 60, 65, 63, 62, 64, 66, 63, 63, 63, 62, 59, 65, 66, 63, 61, 63, 62, 65, 68, 68, 68, 68, 63, 65, 66, 67, 62, 64, 61, 62, 67, 67, 67, 64, 61, 65, 64, 64, 64, 66, 63, 61, 62, 60, 63, 61, 63, 62, 61, 62, 61, 60, 60, 62, 63, 66, 63, 62, 63, 64, 64, 63, 64, 61, 63, 65, 63, 63, 63, 62, 63, 64, 66, 66, 66, 68, 66, 68, 67, 64, 64, 66, 63, 65, 68, 64, 66, 68, 65, 64, 66, 66, 66, 68, 71, 71, 73, 71, 73, 73, 74, 75, 75, 78, 82, 78, 81, 84, 83, 85, 84, 83, 84, 86, 86, 85, 82, 78, 81, 76, 76, 80, 79, 79, 75, 74, 76, 78, 79, 77, 70, 70, 74, 71, 69, 69, 65, 63, 65, 66, 63, 61, 60, 62, 58, 59, 60, 60, 58, 59, 59, 58, 57, 56, 54, 53, 55, 51, 51, 54, 54, 52, 51, 50, 52, 48, 50, 52, 51, 49, 49, 50, 50, 48, 46, 47, 47, 46, 48, 46, 49, 47, 46, 47, 46, 47, 46, 46, 47, 45, 45, 45, 45, 46, 44, 44, 43, 45, 46, 43, 44, 44, 44, 42, 43, 44, 45, 50, 44, 43, 40, 41, 43, 41, 42, 42, 43, 42, 42, 46, 44, 43, 42, 39, 40, 42, 41, 41, 44, 42, 42, 43, 44, 41, 42, 43, 41, 42, 41, 41, 41, 41, 43, 42, 40, 38, 39, 39, 40, 39, 38, 42, 41, 41, 40, 40, 40, 40, 41, 41, 42, 41, 41, 39, 41, 40, 44, 42, 40, 42, 39, 38, 38, 37, 39, 36, 36, 37, 39, 39, 37, 38, 40, 39, 42, 40, 39, 38, 36, 36, 36, 35, 37, 35, 38, 36, 34, 37, 36, 36, 36, 36, 36, 37, 38, 38, 36, 35, 37, 36, 37, 34, 34, 37, 39, 38, 36, 38, 36, 36, 36, 36, 37, 36, 35, 36, 36, 34, 37, 35, 32, 36, 36, 35, 35, 36, 36, 38, 36, 36, 36, 34, 33, 35, 34, 33, 37, 35, 35, 35, 35, 35, 34, 34, 35, 34, 34, 32, 34, 34, 31, 33, 36, 34, 35, 35, 34, 36, 35, 35, 35, 36, 35, 40, 36, 35, 36, 34, 34, 35, 34, 33, 34, 35, 33, 31, 32, 34, 35, 32, 34, 33, 31, 31, 32, 31, 32, 33, 34, 34, 34, 35, 34, 35, 33, 33, 30, 30, 31, 31, 31, 34, 33, 32, 33, 33, 32, 32, 31, 32, 32, 32, 32, 31, 31, 32, 31, 32, 32, 31, 33, 33, 32, 32, 32, 33, 33, 34, 33, 31, 32, 34, 34, 34, 33, 34, 34, 34, 33, 34, 34, 34, 34, 31, 31, 32, 30, 30, 29, 30, 31, 30, 33, 33, 33, 32, 33, 34, 33, 33, 34, 32, 32, 32, 31, 33, 32, 31, 30, 30, 31, 31, 31, 30, 30, 30, 30, 30, 32, 32, 30, 32, 33, 34, 33, 35, 35, 33, 31, 31, 33, 32, 34, 34, 33, 35, 33, 32, 32, 32, 32, 30, 31, 31, 33, 33, 32, 33, 34, 33, 34, 32, 34, 36, 33, 35, 35, 33, 34, 35, 35, 35, 33, 35, 36, 36, 37, 36, 34, 34, 35, 37, 37, 36, 34, 34, 34, 36, 35, 38, 38, 36, 37, 38, 37, 39, 38, 38, 38, 37, 35, 38, 42, 37, 39, 39, 40, 42, 41, 41, 38, 42, 43, 45, 43, 43, 45, 43, 43, 43, 43, 44, 45, 45, 47, 47, 46, 48, 49, 47, 49, 49, 51, 50, 52, 49, 48, 47, 44, 46, 48, 47, 47, 48, 47, 48, 48, 47, 48, 50, 49, 49, 50, 47, 48, 46, 46, 44, 48, 49, 48, 49, 49, 47, 47, 46, 45, 44, 46, 43, 44, 45, 46, 46, 46, 44, 44, 46, 45, 44, 45, 47, 45, 47, 45, 46, 43, 47, 45, 46, 49, 53, 47, 46, 45, 44, 44, 44, 45, 47, 46, 47, 48, 46, 46, 47, 45, 47, 47, 47, 47, 50, 47, 49, 46, 50, 47, 47, 48, 47, 46, 47, 46, 47, 43, 47, 46, 47, 46, 45, 46, 47, 46, 45, 47, 50, 49, 49, 47, 50, 52, 50, 49, 52, 50, 51, 49, 48, 48, 50, 50, 48, 45, 46, 48, 50, 51, 50, 49, 50, 50, 52, 52, 51, 49, 50, 52, 48, 47, 48, 52, 46, 47, 49, 47, 47, 48, 48, 49, 46, 45, 46, 47, 50, 50, 50, 50, 51, 50, 48, 55, 51, 52, 53, 53, 55, 55, 53, 52, 54, 54, 55, 54, 53, 52, 56, 54, 55, 53, 52, 53, 53, 54, 54, 52, 51, 49, 51, 55, 53, 54, 52, 55, 54, 56, 53, 51, 52, 52, 53, 51, 53, 51, 51, 53, 54, 55, 56, 53, 54, 53, 56, 53, 52, 55, 55, 53, 55, 54, 50, 51, 52, 50, 48, 48, 49, 51, 51, 48, 48, 51, 52, 53, 51, 47, 50, 52, 50, 53, 52, 50, 48, 49, 50, 50, 52, 53, 51, 50, 50, 47, 46, 46, 49, 48, 50, 50, 52, 48, 50, 50, 52, 51, 51, 51, 50, 48, 49, 48, 50, 49, 51, 50, 51, 53, 53, 53, 51, 52, 51, 53, 51, 49, 49, 51, 51, 51, 50, 52, 50, 51, 52, 48, 48, 47, 49, 50, 47, 48, 52, 52, 49, 54, 52, 50, 49, 51, 51, 51, 51, 51, 51, 52, 56, 55, 55, 56, 56, 54, 54, 53, 51, 53, 51, 49, 53, 52, 53, 53, 54, 52, 53, 54, 54, 53, 56, 52, 54, 51, 50, 53, 51, 54, 54, 55, 52, 50, 53, 53, 49, 50, 52, 56, 57, 53, 55, 56, 53, 52, 52, 54, 55, 55, 56, 54, 55, 55, 53, 57, 56, 55, 54, 54, 54, 52, 55, 56, 56, 57, 59, 59, 59, 57, 58, 58, 57, 58, 55, 58, 56, 55, 53, 54, 52, 52, 52, 50, 52, 51, 55, 52, 50, 53, 53, 51, 53, 52, 54, 52, 53, 54, 55, 57, 58, 55, 55, 57, 59, 57, 56, 54, 57, 60, 57, 59, 59, 61, 60, 61, 62, 62, 63, 62, 64, 61, 62, 65, 65, 65, 65, 64, 63, 64, 63, 62, 64, 63, 58, 60, 61, 59, 55, 55, 59, 58, 57, 54, 53, 54, 51, 52, 53, 53, 49, 49, 46, 47, 48, 47, 48, 47, 45, 43, 44, 44, 42, 41, 45, 46, 44, 43, 42, 42, 42, 43, 45, 44, 43, 44, 42, 41, 38, 40, 39, 39, 41, 38, 39, 38, 39, 41, 41, 42, 40, 40, 41, 42, 40, 39, 41, 41, 41, 40, 40, 39, 37, 38, 39, 36, 35, 35, 35, 37, 37, 36, 34, 36, 35, 35, 36, 35, 38, 39, 37, 38, 37, 37, 33, 35, 35, 32, 32, 33, 37, 36, 35, 34, 33, 36, 36, 37, 38, 36, 35, 32, 33, 32, 30, 32, 30, 30, 32, 32, 32, 30, 33, 33, 31, 30, 31, 34, 33, 32, 31, 32, 31, 33, 30, 30, 30, 30, 31, 31, 31, 29, 30, 30, 30, 30, 30, 31, 29, 32, 31, 31, 31, 31, 29, 30, 32, 30, 29, 30, 29, 29, 29, 26, 28, 30, 32, 30, 30, 32, 31, 31, 29, 29, 29, 29, 29, 28, 31, 30, 30, 30, 31, 29, 28, 29, 29, 27, 27, 28, 28, 27, 27, 28, 29, 29, 27, 27, 28, 28, 28, 26, 29, 29, 27, 28, 27, 27, 27, 27, 28, 27, 27, 28, 29, 28, 27, 28, 26, 25, 24, 25, 26, 25, 25, 26, 26, 26, 28, 26, 25, 28, 27, 27, 25, 26, 24, 25, 26, 27, 27, 26, 25, 26, 25, 23, 24, 25, 24, 23, 24, 26, 26, 25, 26, 25, 26, 24, 25, 25, 24, 26, 26, 26, 26, 25, 26, 24, 25, 26, 26, 26, 25, 24, 26, 25, 25, 25, 25, 25, 26, 25, 26, 19]

wc_scaled_trace_list = []

# scale down the trace

for index in range(0, len(wc_trace_list)):
    wc_scaled_trace_list.append(int(math.ceil(wc_trace_list[index] / 10)))

goal_list = []
user_goal_file  = open("main_user_goal_file.txt","r")
for goal_line in user_goal_file:
    goal_list.append(goal_line)``



EXPERIMENT_NAME = "sample_experiment_static"



instance = 0
# load the goal file

# The url where the user requests are sent
#service_api_url_list = ["http://localhost:9100/accomplishGoal","http://localhost:9101/accomplishGoal"]
#service_api_url_list = ["http://localhost:9100/accomplishGoal","http://localhost:9101/accomplishGoal","http://localhost:8101/accomplishGoal","http://localhost:8100/accomplishGoal"]



function_flow_list = ["http://localhost:8894/checkAvailableBooking","http://localhost:8894/requestBooking", "http://localhost:8892/recomendParking","http://localhost:8890/getWeather"]
function_flow_list2 = ["http://localhost:7774/checkAvailableBooking","http://localhost:7774/requestBooking","http://localhost:7772/recomendParking", "http://localhost:7780/getWeather"]




service_api_url_list = ["http://localhost:9100/accomplishGoal","http://localhost:8100/accomplishGoal"]
# IN the static part we simulate in such a way that any goal is given a sequential behaviour and based on number of goals there shall be an added delay given
#adaptation_type = "noadap_static_clarknet" # noadap indicates the baseline with no adaptations done
adaptation_type = "adap_static" # noadap indicates the baseline with no adaptations done

sql_obj = SQLUtils()

count = 0


def goal_type_identifier(goal_text):
    # Identify the type of goal first if it is one of, sequence, AND based , OR based or just one
    if "one of" in goal_text:
        return "oneof"
    elif "seq" in goal_text:
        return "seq"
    elif "and" in goal_text:
        # one can write this rule as "AND" and "OR" to identiy if is AND OR based goal
        return "and"
    elif "or" in goal_text:
        return "or"
    else:
        # just one goal
        return "single"

def fetch(session, goal):
    print ("goal ",goal)

    #instance = random.randint(0,len(service_api_url_list)-1)
    # round robin implementation

    with session:
        global  instance
        # for every goal the activity is assumed to be a sequence
        len_val = len(function_flow_list)
        # check the type of goal
        # if it is sequence


        # based on the goal string understand, till which part the functionality needs to be executed
        goal_json = parse_obj.goal_string_generator(goal)
        if goal_json["goal_type"] == "and" or goal_json["goal_type"] == "seq":
            len_val = 4
        elif goal_json["goal_type"] == "or" or goal_json["goal_type"] == "oneof" or goal_json["goal_type"]== "single":
            goal_key = goal_json["goal_string"][0]
            if goal_key == "0":
                len_val = 3
            elif goal_key == "1":
                len_val = 4
            elif goal_key == "2":
                len_val = 2
            else:
                len_val = 1
        instance += 1
        if instance > 1:
            instance = 0


        print ("instance ", instance)
        start_time = time.time()
        print ("len val ",len_val)
        for index in range(0,len_val):
            if instance > 1:
                response = requests.post(function_flow_list[index],json.dumps(json_data))
            else:
                response = requests.post(function_flow_list2[index], json.dumps(json_data))


        end_time = time.time()
        timediff = (end_time - start_time)
        goal_string = str(len_val)     # keep track on where the sequence terminated or if it was full execution

        #if (len_val > 1):
        #    timediff = timediff + len_val*0.1  # Add a small amount of thinking time if there are sequential goals

        goal_type = "staticflow"   # the type of goal flow is static
        query = "insert into user_goal_logs(goal,goal_type,experiment,latency) values(" + "'" + str(
            goal_string) + "','" + str(goal_type) + "'," + "'" + EXPERIMENT_NAME + "'," + str(timediff) + ");"
        # print (query)
        sql_obj.insert(query)
        print("inserted ", str(timediff))

        #print ("len val " , len_val, (end_time-start_time).microseconds/1000000)

async def get_data_asynchronous(count,start,end):
    #print("{0:<30} {1:>20}".format("File", "Completed at"))
    with ThreadPoolExecutor(max_workers=count) as executor:
        with requests.Session() as session:
            # Set any session parameters here before calling `fetch`
            loop = asyncio.get_event_loop()

            tasks = [
                loop.run_in_executor(
                    executor,
                    fetch,
                    *(session, goal) # Allows us to pass in multiple arguments to `fetch`
                )
                for goal in goal_list[start:end]
            ]
            for response in await asyncio.gather(*tasks):
                #print (response)
                pass

def main():
    instance = 0
    loop = asyncio.get_event_loop()
    start = 0
    end = 0
    start_time = time.time()
    program_start = datetime.now()
    flag = 0
    while(True):
        if flag == 1:
            break
        for wc_trace in wc_scaled_trace_list:
            current_time = time.time()
            elapsed_time = current_time - start_time
            if elapsed_time >=18000:
                flag = 1
                break
            print ("elapsed time", elapsed_time)
            start = end
            end = start + wc_trace
            try:
                future = asyncio.ensure_future(get_data_asynchronous(wc_trace, start, end))
                loop.run_until_complete(future)
            except:
                pass




main()
