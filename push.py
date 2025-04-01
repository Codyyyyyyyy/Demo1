from git import Git, Repo

local_repo_path = r'C:\automation.air_mumu'
remote_repo_url = 'git@github.com:Codyyyyyyyy/Demo1.git'
try:
    # 打开本地仓库
    repo = Repo(local_repo_path)
    repo.git.add(all=True)
    repo.index.commit('Daily Update')
    # 使用Git对象执行推送操作
    g = Git(repo.working_dir)
    g.push(remote_repo_url)
    print('push success')
except Exception as e:
    print(f'Something goes wrong:{e}')