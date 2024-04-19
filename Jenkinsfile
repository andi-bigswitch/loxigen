// calculate maven patch version for Maven CI friendly revision
def getMavenPatchVersion() {
    switch(env.JOB_BASE_NAME) {
        case "master":
            // for master, just the build number (these are our "production" releases)
            return env.BUILD_NUMBER
        case ~/PR-\d+/:
            // for PRs, we use SNAPSHOTS
            return "${env.JOB_BASE_NAME}-SNAPSHOT"
        default:
            // for other branches "branchname".number
            return "${env.JOB_BASE_NAME}.${env.BUILD_NUMBER}"
    }
}

mavenPatchVersion=getMavenPatchVersion()
artifact_repo="git@github.com:bigswitch/loxigen-artifacts.git"
artifact_base_branch=env.CHANGE_TARGET ?: env.JOB_BASE_NAME
artifact_target_branch= env.CHANGE_ID ? "${env.JOB_BASE_NAME}-b${env.BUILD_NUMBER}" : env.JOB_BASE_NAME

@Library("github") _

if(env.CHANGE_ID) {
    withCredentials([string(
                credentialsId: 'github-auth-token-bsn-abat',
                variable: 'GITHUB_AUTH_TOKEN') ]) {
        githubCheckOrgAuthz(env.CHANGE_URL, env.GITHUB_AUTH_TOKEN)
    }
}

pipeline {
    agent {
        dockerfile {
            dir 'docker'
            args """--entrypoint ''"""
        }
    }
    options {
        ansiColor('xterm')
        timestamps()
    }
    parameters {
        string(
            name: 'LOXI_COMMIT',
            defaultValue: '',
            description: '''
            Specify commit sha to build
            ''',
        )
        string(
            name: 'OPENFLOWJ_VERSION',
            defaultValue: '',
            description: '''
            Specify full version string to use for openflowj. (3.7.42-SNAPSHOT, 3.8.42)
            ''',
        )
    }

    stages {
        stage("Prepare") {
            steps {
                echo "Maven Patch Version: ${mavenPatchVersion}"
                echo "artifact_base_branch: ${artifact_base_branch}"
                echo "artifact_target_branch: ${artifact_target_branch}"
                echo "LOXI_COMMIT: ${LOXI_COMMIT}"
                echo "OPENFLOWJ_VERSION: ${OPENFLOWJ_VERSION}"
            }
        }

        stage("Checkout infrastructure") {
            steps {
                sshagent(['ssh_jenkins_master']) {
                    dir('infrastructure') {
                        git(credentialsId: 'ssh_jenkins_master', url: 'git@github.com:bigswitch/infrastructure.git')
                    }
                }
            }
        }

        stage("Clean") {
            steps {
                sh """
                    make clean
                    """
            }
        }

        // build the source in 'build' to allow use of latest build pipeline with past commit
        stage("Checkout source (default)") {
            when { environment name: 'LOXI_COMMIT', value: ''}
            steps {
                // if not specifying specific commit, symlink 'build' to workspace home
                sh """
                if [ ! . -ef build ]; then
                    rm -rf build
                    ln -s . build
                fi
                """
            }
        }
        stage("Checkout source (alternative)") {
            when { not { environment name: 'LOXI_COMMIT', value: ''} }
            steps {
                dir("build") {
                    checkout(
                        poll: false,
                        scm: scmGit(
                            branches: [[name: '${LOXI_COMMIT}']],
                            extensions: [localBranch('build')],
                            userRemoteConfigs: [[credentialsId: 'ssh_jenkins_master', url: 'git@github.com:bigswitch/loxigen.git']])
                    )
                }
            }
        }

        stage("Build") {
            steps {
                dir("build") {
                    sh """
                        make clean all
                        """
                }
            }
        }

        stage("Unit tests") {
            steps {
                dir("build") {
                    dir('loxi_output/openflowj/.mvn/') {
                        // maven config overrides to let older commits use current proxy
                        writeFile(
                            file: 'settings.xml',
                            text: """
                            <settings>
                                <mirrors>
                                    <mirror>
                                    <id>artifactory-proxy</id>
                                    <url>https://artifactory.infra.corp.arista.io/artifactory/bsn-proxy-virtual/</url>
                                    <mirrorOf>*</mirrorOf>
                                    </mirror>
                                </mirrors>
                            </settings>
                            """
                        )
                        writeFile(
                            file: 'maven.config',
                            text: """
                            --settings
                            ./.mvn/settings.xml
                            """
                        )
                    }
                    dir('loxi_output/openflowj') {
                        // if there's version override, apply
                        sh """
                        if [ -n "${OPENFLOWJ_VERSION}" ]; then
                            mvn --batch-mode -V versions:set -DnewVersion=${OPENFLOWJ_VERSION}
                        fi
                        """
                    }
                    sh """
                        make check check-all
                        """
                }
            }
        }

        stage("Generate Artifacts") {
            steps {
                sshagent(['ssh_jenkins_master']) {
                    dir("build") {
                        sh """
                            ./.build/push-artifacts.sh ${artifact_repo} ${artifact_base_branch} ${artifact_target_branch}
                        """
                    }
                }
           }
        }

        stage("Artifact Link") {
            when { branch 'PR-*' }
            steps {
                withCredentials([string(
                            credentialsId: 'github-auth-token-bsn-abat',
                            variable: 'GITHUB_AUTH_TOKEN') ]) {
                    sh """
                        ./infrastructure/build/githubtool/gh.py comment "Find artifact changes from this pull request at https://github.com/bigswitch/loxigen-artifacts/tree/${artifact_target_branch}"
                        """
                }
            }
        }

        stage("Deploy OpenflowJ") {
            steps {
                withCredentials([file(credentialsId: 'maven-code-signing-key', variable: 'MAVEN_SIGNING_KEY_FILE')]) {
                    sh 'gpg --fast-import <$MAVEN_SIGNING_KEY_FILE'
                }
                dir("build") {
                    configFileProvider( [configFile(fileId: 'maven-settings-xml', variable: 'MAVEN_SETTINGS')]) {
                        sh """#!/bin/bash
                            set -x
                            set -e
                            make clean java
                            cd loxi_output/openflowj
                            deployTo="internal::default::https://artifactory.infra.corp.arista.io/artifactory/bsn-internal-local/"
                            if [ -n "${OPENFLOWJ_VERSION}" ]; then
                                mvn --batch-mode -V -s $MAVEN_SETTINGS versions:set -DnewVersion=${OPENFLOWJ_VERSION}
                                if [[ "${OPENFLOWJ_VERSION}" =~ -SNAPSHOT ]]; then
                                    deployTo="snapshots::default::https://artifactory.infra.corp.arista.io/artifactory/bsn-snapshots-local/"
                                fi
                            else
                                if [[ "${mavenPatchVersion}" =~ -SNAPSHOT ]]; then
                                    deployTo="snapshots::default::https://artifactory.infra.corp.arista.io/artifactory/bsn-snapshots-local/"
                                fi
                            fi
                            mvn --batch-mode -V -s $MAVEN_SETTINGS -DaltDeploymentRepository=\$deployTo -Prelease -Psign -Drevision=${mavenPatchVersion} deploy
                        """
                    }
                }
            }
            post {
                cleanup {
                    sh """
                        gpg --batch --yes --delete-secret-key 'EF31 1B74 EE63 3982 2335  F1B2 68B8 8023 E9F9 33D3'
                    """
                }
            }
        }
    }
}
