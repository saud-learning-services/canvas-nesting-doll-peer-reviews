"""
authors:
@markoprodanovic, @alisonmyers
"""

import settings
import pandas as pd
from helpers import _return_single_dict_match
from util import shut_down
from pick import pick
from canvasapi import Canvas
from termcolor import cprint
import os
from dotenv import load_dotenv
load_dotenv() 

URL = os.getenv('API_URL')
KEY = os.getenv('API_TOKEN')

def _get_groups(course):
    groups = course.get_group_categories()
    groups_list = [i.__dict__ for i in groups]
    groups_df = pd.DataFrame(groups_list)[["id", "name"]]
    
    return(groups_df, groups_list)

def get_user_inputs(URL, KEY):
    """Prompt user for required inputs. Queries Canvas API throughout to check for
    access and validity errors. Errors stop execution and print to screen.

    Returns:
        Dictionary containing inputs
    """

    # prompt user for url and token
    url = URL
    token = KEY

    # Canvas object to provide access to Canvas API
    canvas = Canvas(url, token)

    # get user object
    try:
        user = canvas.get_user("self")
        cprint(f"\nHello, {user.name}!", "green")
        # shut_down('TEMP KILL SWITCH')
    except Exception as e:
        shut_down(
            """
            ERROR: could not get user from server.
            Please ensure token is correct and valid and ensure using the correct instance url.
            """
        )

    # get course object
    try:
        course_number = input("Course Number: ")
        course = canvas.get_course(course_number)
    except Exception as e:
        shut_down("ERROR: Course not found. Please check course number.")

    # get how to assign peer reviews
    try:
        title = "Please select how you to get student information for assigning peer reviews"
        options = ["group", "assignment"]
        peer_reviews_from = pick(options, title, multiselect=False, min_selection_count=1)

        
        settings.PR_SOURCE = peer_reviews_from[0]

        #if groups then
        if peer_reviews_from[1] == 0:

            try:
                title = "Please select which Canvas Group Set to use"
                groups_df, groups_list = _get_groups(course)
                print(groups_df)
                
                canvas_group_category_id = input("Please enter the Canvas group category id: ")
                #settings.PR_COURSE = "group"
                #canvas_group_category = _return_single_dict_match(groups_list, "id", canvas_group_category_id)
                #_prompt_for_confirmation([("Canvas Group Selected",  canvas_group_category)])
                #settings.GROUP_PR = canvas_group_category
                #peer_review_source = settings.GROUP_PR 
                #print(settings.GROUP_PR)
                shut_down("Doesn't work yet. Whoops")

            except Exception as e:
                shut_down(f"ERROR accessing Canvas groups. {e}")
            
        else:

            try:
                assignment_id_peerreviews = input("Please enter the assignment_id to access original peer reviews for: ")
                assignment_peerreview = course.get_assignment(assignment_id_peerreviews)
                settings.ASSIGNMENT_PR = assignment_peerreview

            except:
                shut_down("ERROR: error getting original peer review info.")
    except:

        shut_down("ERROR: need to enter how you will get data for peer reviews")

    # get assignment object
    try:
        assignment_number = input("Please Enter the Assignment for the New Peer Reviews ")
        assignment = course.get_assignment(assignment_number)

    except Exception as e:
        shut_down("ERROR: Assignment not found. Please check assignment number.")

    # prompt user for confirmation


    # set course and assignment objects to global variables
    settings.COURSE = course
    settings.ASSIGNMENT = assignment

    # return inputs dictionary
    return

def _prompt_for_confirmation(confirmationList=[], *args):
    """Prints user inputs to screen and asks user to confirm. Shuts down if user inputs
    anything other than 'Y' or 'y'. Returns otherwise.

    Args:
        a list of tuples: [(input_string, value)]
    Returns:
        None -- returns only if user confirms

    """
    cprint("\nConfirmation:", "blue")

    for i in confirmationList:
        cprint(f"{i[0]}: {i[1]}", "blue")
    print("\n")

    confirm = input("Would you like to continue using the above information?[y/n]: ")

    print("\n")

    if confirm == "y" or confirm == "Y":
        return
    elif confirm == "n" or confirm == "N":
        shut_down("Exiting...")
    else:
        shut_down("ERROR: Only accepted values are y and n")