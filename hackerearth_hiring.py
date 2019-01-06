import requests
import json
import os
import traceback
from bs4 import BeautifulSoup


def main():
    '''
    main function where the script starts to execute.
    '''
    base_url = "http://hck.re/crowdstrike"
    request_headers = {
    }
    error, web_scraper_data = web_scraper(req_url=base_url)
    if not error:
        try:
            file_download = download_file_to_commit()
            if not file_download:
                print("Some error occured while downloading file to commit to git repo !!")
            else:
                for scraper_item in web_scraper_data:
                    # iterating over scraped data
                    repo_name = scraper_item.get('Repo Name')
                    repo_git_url = scraper_item.get('Repo Url')
                    repo_branch = scraper_item.get('Branch Name')

                    clone_git = clone_git_repo(repo_git_url, repo_name)
                    repo_branches = get_repo_branch_info(repo_name=repo_name)

                    if not clone_git:
                        print(
                            "Some error occurred while trying to clone repo : {0}".format(repo_name))
                    else:
                        add_file = add_file_to_repo(
                            repo_name=repo_name, repo_branches=repo_branches, checkout_branch=repo_branch)
                        if not add_file:
                            print("error occured while adding file to repo : {0}".format(repo_name))
                        else:
                            "file added and pushed successfully to remote host server."

        except Exception as e:
            print("Some error occurred !!!", "\n")
            raise e


def add_file_to_repo(repo_name=None, repo_branches=None, checkout_branch=None):
    '''
    function to add the file to git in a given repo, committing it and finally pushing that branch to remote Host.
    If the user has access to the Host git server, then only he/she can push to the host repo.
    '''
    try:
        current_directory = os.getcwd()

        # moving the file to be added in the specific repo folder.
        cp_command = 'cp response.js ' + str(repo_name)
        os.system(cp_command)

        repo_directory = current_directory + '/' + repo_name
        os.chdir(repo_directory)

        # check out new branch
        # if this branch is already there, then ask user is asked to take a
        # pull/rebase of their local branch & then proceed.
        user_input = 'yes'
        if str(checkout_branch) in repo_branches:
            user_input = input(
                "The branch we are trying to checkout already exists in remote host, so please make sure that your local branch is upto date with remote, if ready press yes , if not press no")
        if str(user_input) == 'yes':
            branch_checkout_command = 'git checkout -b ' + checkout_branch
            os.system(branch_checkout_command)

            # adding file to git
            os.system('git add response.js')

            # git commit
            commit_command = 'git commit -m "added file response.js to repo"'
            os.system(commit_command)

            # pushing branch to remote Host
            push_command = 'git push origin ' + checkout_branch
            os.system(push_command)

            # again moving to root directory
            os.chdir(current_directory)
            return True
        return False
    except Exception as e:
        traceback.print_exc()
        return False


def get_repo_branch_info(repo_name=None):
    '''
    function to get all the branches of a repo.
    Reason :
        so that if a branch that the user needs to push is already present in Host repo, then the user can be notified
        that to update their local branch either by taking git pull or git rebase. 
    '''
    try:
        branches = []
        req_url = "https://api.bitbucket.org/2.0/repositories/zeeshan_07/" + \
            str(repo_name) + "/refs/branches"
        res = requests.get(req_url)
        if res.status_code in [200]:
            res = res.json()
            if res and 'values' in res:
                branch_list = res['values']
                for item in branch_list:
                    if item.get('type') == 'branch':
                        branches.append(item.get('name'))
        return branches
    except Exception as e:
        return None


def clone_git_repo(repo_url=None, repo_name=None):
    '''
    function to clone the git repo.
    '''
    try:
        clone_command = 'git clone ' + str(repo_url) + ' ' + repo_name
        os.system(clone_command)
        return True
    except Exception as e:
        return False


def download_file_to_commit():
    '''
    function to download the file which will be added to the git repo.
    '''
    try:
        url = 'http://hck.re/tHEZGP'
        r = requests.get(url, allow_redirects=True)
        open('response.js', 'wb').write(r.content)
        return True
    except Exception as e:
        return False


def web_scraper(req_url=None):
    '''
    function to scrape data from the given URL.
    '''
    try:
        html_request = requests.get(req_url)
        html = BeautifulSoup(html_request.text, 'html.parser')
        res = []
        if html:
            nav = html.find_all('tr')
            header_list = nav[0].find_all('th')
            headers = []
            for item in header_list:
                headers.append(item.text)
            if len(nav) > 1:
                for item in nav[1:]:
                    res_dict = {}
                    item_data_list = item.find_all('td')
                    for cnt, i in enumerate(item_data_list):
                        res_dict[headers[cnt]] = str(i.text)
                    res.append(res_dict)
            return (False, res)
        return (False, None)
    except Exception as e:
        print("Some error occurred man !!!")
        return (True, None)

if __name__ == "__main__":
    main()
