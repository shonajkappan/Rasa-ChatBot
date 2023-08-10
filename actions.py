# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
import os
import csv
#import pandas as pd
from flask import Flask
from flask_cors import CORS
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List
from datetime import datetime, timedelta
import re
import nltk
from nltk.corpus import stopwords

# Download the NLTK stopwords if not already downloaded
nltk.download('stopwords')



app = Flask(__name__)
CORS(app)
# Assuming you have loaded the DataFrame and named it 'udemy_df'
# Replace 'your_dataframe_path_or_creation_logic' with the actual DataFrame path or creation logic
# Example: 'udemy_df = pd.read_csv('filename.csv')'
#udemy_df = pd.read_csv("C:\Rasa\chatbot\actions\new_data.csv")

class SharedContext:
    data = {}



class PrintExecutedStoryAction(Action):
    def name(self) -> Text:
        return "action_print_executed_story"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        executed_story = tracker.export_stories()
        print("\nExecuted Story:\n", executed_story)
        return []
    
class ActionFindPaidCourses(Action):
    def name(self) -> Text:
        return "action_find_paid_courses"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        # Get the extracted entity value from the user's message
        topic_value = tracker.get_slot("topic")
        paid_value = tracker.get_slot("is_paid")
        if paid_value in ['yes','YES','no','NO','No','paid','nope','yeah','yup','unpaid']:
            print("hhjsfhjshfjdfhslfj")
            courses = self._search_courses_by_topics(topic_value,paid_value)
            if not courses:
            # If no courses found for the topics, send a response indicating that
                dispatcher.utter_message("I couldn't find any courses related to this topics.Please search another similar topic!or further details reach our helpdesk at *****@gmail.com")
            else:
            # If courses found, create a response message and send it to the user
                course_list = "\n".join([f"{index + 1}: <a href='{course['url']}'>{course['course_title']}</a> \n" for index, course in enumerate(courses)])
                response = f"These are the top trending courses as per your request:\n{course_list}"
                dispatcher.utter_message(response)
            
        # # Generate the dynamic response using the extracted entity value
        # dynamic_response = f"Your selected topic is {topic_value}. This is a dynamic response."

        # # Send the response back to the user
        # dispatcher.utter_message(text=dynamic_response)
        else:
            dispatcher.utter_message("Enter valid input.(Yes/No)")
        
        return []
        
    def _search_courses_by_topics(self, topics,is_paid):
        courses = []
        print(topics,is_paid)
        course_title= SharedContext.data
        is_paid_string = 'True' if is_paid.lower() in ['yes', 'paid'] else 'False'
        for ct in course_title:
            if(ct['is_paid'].lower()==is_paid_string.lower() ):
                courses.append(ct)
                
        if not course_title:
            print("no course title")
            current_directory = os.path.dirname(__file__)
            csv_file_path = os.path.join(current_directory, "new_data(2).csv")
            with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # print(row["Topics"])         
                    row_topics = [t.strip() for t in row["Topics"].split(",")]
                    paid_topic= [row["is_paid"]]
                    converted_paid = ['yes' if item == 'True' or item == 'paid' else 'no' for item in paid_topic]

                    #converted_paid = ['yes'|'paid' if item == 'True' else 'no' for item in paid_topic]

                    if  any(topics.lower() in row_topics for topic in topics):
                        if(is_paid.lower() in converted_paid):
                            courses.append(row)
        course_sorted=sorted(courses, key=lambda x: int(x['num_subscribers']),reverse=True)
        return course_sorted[:5]
    


class ActionRespondWithTopic(Action):
    def name(self) -> str:
        return "action_respond_with_topic"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        # Get the extracted entity value from the user's message
        topic_value = tracker.get_slot("topic")
        courses = self._search_courses_by_topics(topic_value)
        if not courses:
            # If no courses found for the topics, send a response indicating that
            dispatcher.utter_message("I couldn't find any courses related to this topics.Please search another similar topic!or further details reach our helpdesk at *****@gmail.com")
        else:
            # If courses found, create a response message and send it to the user
            course_list = "\n".join([f"{index + 1}: <a href='{course['url']}'>{course['course_title']}</a> \n" for index, course in enumerate(courses)])
            response = f"Here are the top trending courses related to {''.join(topic_value)} Click for more details:\n{course_list}.  \n Are you looking for paid courses?"
            dispatcher.utter_message(response)
 
        # Generate the dynamic response using the extracted entity value
        #dynamic_response = f"Your selected topic is {topic_value}. Do you want to know about paid courses."

        # Send the response back to the user
        #dispatcher.utter_message(text=dynamic_response)

        return []
        
    def _search_courses_by_topics(self, topics):
        courses = []
        SharedContext.data.clear()
        print(topics)
        current_directory = os.path.dirname(__file__)
        csv_file_path = os.path.join(current_directory, "new_data(2).csv")
        with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # print(row["Topics"])         
                row_topics = [t.strip() for t in row["Topics"].split(",")]
                if  any(topics.lower() in row_topics for topic in topics):
                    courses.append(row)
                row_subject = [t.strip().lower() for t in row["subject"].split(" ")]
                if  any(topics.lower() in row_subject for topic in topics): 
                    courses.append(row)
            course_sorted=sorted(courses, key=lambda x: int(x['num_subscribers']),reverse=True)
        return course_sorted[:5]

class CoursePrintUserInput(Action):
    def name(self):
        return "action_course_print_user_input"

    def run(self, dispatcher, tracker, domain):
        user_input = tracker.latest_message.get("text")
        predefined_words = []
        user_input_tokens = user_input.lower().split()
        print("User Input:", user_input)
        stop_words = set(stopwords.words('english'))
        matching_words = [word for word in user_input_tokens if word not in predefined_words and word not in stop_words]
        print("Matching words:", matching_words)
        courses = self._search_courses_by_titles(matching_words)
        if not courses:
            # If no courses found for the topics, send a response indicating that
            dispatcher.utter_message("I couldn't find any courses related to this topics.Please search another similar topic!or further details reach our helpdesk at *****@gmail.com")
        else:
            # If courses found, create a response message and send it to the user
            course_list = "\n".join([f"{index + 1}: <a href='{course['url']}'>{course['course_title']}</a> \n" for index, course in enumerate(courses)])
            response = f"Here are the most trending courses related to your topic, Click for more details:\n{course_list}.  \n Are you looking for paid courses?"
            dispatcher.utter_message(response)
 
        return []
    
    def _search_courses_by_titles(self, topics):
        courses = []
        #print(topics)
        predefined_words = []
        current_directory = os.path.dirname(__file__)
        csv_file_path = os.path.join(current_directory, "new_data(2).csv")
        with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # print(row["Topics"])  
                course_title_tokens = row["course_title"].lower().split()
                stop_words = set(stopwords.words('english'))
                cousre_words = [word for word in course_title_tokens if word not in predefined_words and word not in stop_words]
                if sum(item in cousre_words for item in topics) >= 2:
                    
                # if cousre_words == topics:
                    #print("yes found some course")
                    courses.append(row)
            course_sorted=sorted(courses, key=lambda x: int(x['num_subscribers']),reverse=True)
            #print(course_sorted[:5])
        SharedContext.data = courses
        return course_sorted[:5]   
    
    
    
class ActionFindGreaterDurationCourses(Action):
    def name(self) -> Text:
        return "action_find_greater_duration_courses"
    
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        
            time = tracker.get_slot("user_input_time")
            condition = tracker.get_slot("condition")
            #print('time',time)
            courses = self._search_courses_greater_duration(time,condition)
            if not courses:
            # If no courses found for the topics, send a response indicating that
                dispatcher.utter_message("I couldn't find any courses")
            else:
            # If courses found, create a response message and send it to the user
              course_list = "\n".join([f"{index + 1}. {course['course_title']}: {course['url']}:{course['content_duration']}\n" for index, course in enumerate(courses)])
              response = f"Check the below courses with duration:\n{course_list}"
              dispatcher.utter_message(response)
              
    def string_to_seconds(self,time_string):
        if(time_string!='0'):
            #print(time_string)
            time_string = re.sub(r'(\d+)', r' \1 ', time_string)
            time_string=re.sub(r'(\d+(\.\d+)?)', r'\1 ', time_string)
            parts = time_string.split()
            # print(parts)
            
            total_seconds = 0
            
            for i in range(0, len(parts), 2):
                value = int(parts[i])
                unit = parts[i + 1]

                if unit in ['second', 'seconds']:
                     total_seconds += value
                elif unit in ['minute', 'minutes']:
                    total_seconds += value * 60
                elif unit in ['hour', 'hours']:
                    total_seconds += value * 3600
                elif unit in ['day', 'days']:
                     total_seconds += value * 86400
            # You can add more units here, like weeks, months, etc., if needed

            return total_seconds
        
    def _search_courses_greater_duration(self, user_input_time,condition):
            courses = []
            #print(user_input_time)
            current_directory = os.path.dirname(__file__)
            csv_file_path = os.path.join(current_directory, "new_data(2).csv")
            with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    row_time = row['content_duration']
                    if(row_time!='0'):
                        # print(row_time)
                        ut=float(self.string_to_seconds(user_input_time))
                        rt=float(self.string_to_seconds(row_time))
                        if rt > ut and condition in ['greater than', 'more than','greater','more','higher','high']:
                             courses.append(row)
                        if rt < ut and condition in ['less than','less','lower','lower than','small','smaller than']:
                             courses.append(row)
                #print(courses)
                course_sorted=sorted(courses, key=lambda x: int(x['num_subscribers']),reverse=True)
            return course_sorted[:5]
        
        
class ActionFindsameDurationCourses(Action):
    def name(self) -> Text:
        return "action_find_same_duration_courses"
    
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        
        time = tracker.get_slot("user_input_time")
            
        courses = self._search_courses_same_duration(time)
        if not courses:
            
            dispatcher.utter_message("I couldn't find any courses")
        else:
            course_list = "\n".join([f"{index + 1}: <a href='{course['url']}'>{course['course_title']}</a> : {course['content_duration']}  \n" for index, course in enumerate(courses)])
           
            #course_list = "\n".join([f"{index + 1}. {course['course_title']}: {course['url']}:{course['content_duration']}\n" for index, course in enumerate(courses)])
            response = f"These are top trending courses with this duration:\n{course_list}"
            dispatcher.utter_message(response) 
            
    def string_to_seconds(self,time_string):
        if(time_string!='0'):
            #print(time_string)
            time_string = re.sub(r'(\d+)', r' \1 ', time_string)
            time_string=re.sub(r'(\d+(\.\d+)?)', r'\1 ', time_string)
            parts = time_string.split()
            # print(parts)
            
            total_seconds = 0
            
            for i in range(0, len(parts), 2):
                value = int(parts[i])
                unit = parts[i + 1]

                if unit in ['second', 'seconds']:
                     total_seconds += value
                elif unit in ['minute', 'minutes']:
                    total_seconds += value * 60
                elif unit in ['hour', 'hours']:
                    total_seconds += value * 3600
                elif unit in ['day', 'days']:
                     total_seconds += value * 86400
            # You can add more units here, like weeks, months, etc., if needed

            return total_seconds
        
    def _search_courses_same_duration(self, user_input_time):
        courses = []
        
        current_directory = os.path.dirname(__file__)
        csv_file_path = os.path.join(current_directory, "new_data(2).csv")
        with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row_time = row['content_duration']
                if(row_time!='0'):
                        
                    ut=float(self.string_to_seconds(user_input_time))
                    rt=float(self.string_to_seconds(row_time))
                       
                    if (rt==ut):
                
                        courses.append(row)
                #print(courses)
            course_sorted=sorted(courses, key=lambda x: int(x['num_subscribers']),reverse=True)
        return course_sorted[:5]
    
class ActionFindMinSubCourses(Action):
    def name(self) -> Text:
        return "action_find_no_subscribers"
    
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        
        minSub = tracker.get_slot("minSub")
        print(minSub)    
        courses = self.search_courses_by_min_subscribers(minSub)
        if not courses:
            
            dispatcher.utter_message("I couldn't find any courses")
        else:
            course_list = "\n".join([f"{index + 1}: <a href='{course['url']}'>{course['course_title']}</a> : {course['num_subscribers']} Subscribers \n" for index, course in enumerate(courses)])
           
            response = f"Here are most trending courses with more than {''.join(minSub)} subscribers:\n{course_list}"
            dispatcher.utter_message(response)     


    def search_courses_by_min_subscribers(self,min_subscribers):
        courses = []
        current_directory = os.path.dirname(__file__)
        csv_file_path = os.path.join(current_directory, "new_data(2).csv")
        with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if int(row['num_subscribers']) > int(min_subscribers):
                    courses.append(row)
            course_sorted = sorted(courses, key=lambda x: int(x['num_subscribers']), reverse=True)
        return course_sorted[:10]  # Return the top 10 courses with more subscribers that meet the condition