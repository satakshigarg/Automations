import json
from github import Github
import random as rn
import requests
import gspread
from config import *
from oauth2client.service_account import ServiceAccountCredentials

TOKEN = "GITHUB Repo Token"
acc = Github(TOKEN)
organization = "ORG NAME"
org = acc.get_organization(organization)
# Get all repositories under the organization
repos = org.get_repos(type='all')
Repos = []
for r in repos:
    Repos.append(r.name)

# Get the values of the row as a list
all_sub_teams = sheet1.row_values(3)
sub_teams = [value for value in all_sub_teams if value]

Labels = []
for st in sub_teams:
    Labels.append("IN-" + st)

all_sub_leads = sheet1.row_values(4)
sub_leads = [value for value in all_sub_leads if value]

label_assignee = {}

for i in range(len(Labels)):
    label_assignee[Labels[i]] = sub_leads[i]

# Get the values of the name and GitHub ID columns as lists
name = sheet2.col_values(3)[1:]
github_id = sheet2.col_values(6)[1:]

name_to_github_id = {}
for name, github_id in zip(name, github_id):
    if name in sub_leads:
        name_to_github_id[name] = github_id

# update the content of the json files locally
def assign_random_intern(intern_list, pr):
    gh_ids = list(intern_list.keys())
    weights = tuple(intern_list.values())
    random_intern = rn.choices(gh_ids, weights=weights, k=1)[0]
    print(random_intern)
    pr.add_to_assignees(random_intern)


def pr_assigner(all_interns, rate):
    for r in Repos:
        repo = acc.get_repo(organization + '/' + r)
        pull_requests = repo.get_pulls(state="open", sort="created")

        all_data_load = json.loads(all_interns)

        intern_assign_rates = json.loads(rate)

        all_pocs = all_data_load.keys()
        all_devs = all_data_load.values()
        for pr in pull_requests:
            flag = 0
            assignee_length = [assignee.login for assignee in pr.assignees]
            # Check if the PR has the specific label for sub-team assignment
            if pr.user.login in github_id and any(label.name in Labels for label in pr.labels):
                # Get the sub-team label
                assigned_labels = set()
                for label in pr.labels:
                    for lab in Labels:
                        if lab == label.name and lab not in assigned_labels:
                            subteam_label = label.name
                            assigned_labels.add(label.name)
                            # Find the sub-team lead assigned to the sub-team label
                            subteam_lead = label_assignee[subteam_label]

                            if subteam_lead and subteam_lead in name:
                                # Assign the sub-team lead to the PR
                                pr.add_to_assignees(name_to_github_id[subteam_lead])
                                print(f"Assigned to Sub-team Lead: {subteam_lead}")
                                flag = 1
                            break

            if len(assignee_length) == 0 and flag == 0:
                print(pr.title)
                for all_dev, all_poc in zip(all_devs, all_pocs):
                    if pr.user.login in all_dev:
                        pr.add_to_assignees(all_poc)
                        print(all_poc)
                        flag = 1
                        break
                if flag == 0:
                    print("No POC assigned")
                    assign_random_intern(intern_assign_rates, pr)
