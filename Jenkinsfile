pipeline {
    agent any

    environment {
        SONARQUBE_ENV = 'MySonarQubeServer'
        PATH = "/opt/sonar-scanner/bin:$PATH"
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'master', url: 'https://github.com/Agarwalpriyanshuu/ecom.git', credentialsId: 'git-token'
            }
        }

        stage('Setup Python Virtual Environment') {
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install --break-system-packages --upgrade pip
                pip install --break-system-packages -r requirements.txt

                '''
            }
        }

        stage('Run Pytest') {
            steps {
                sh '''
                . venv/bin/activate
                venv/bin/pytest --maxfail=1 --disable-warnings --junitxml=report.xml
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv("${SONARQUBE_ENV}") {
                    withCredentials([string(credentialsId: 'sonarqube-token', variable: 'SONAR_TOKEN')]) {
                        sh '''
                        . venv/bin/activate
                        sonar-scanner -Dsonar.login=$SONAR_TOKEN
                        '''
                    }
                }
            }
        }

        stage('SAST Scan (Bandit)') {
            steps {
                sh '''
                . venv/bin/activate
                bandit -r . -f json -o bandit-report.json || true
                '''
            }
        }

        stage('Generate SBOM (Syft)') {
            steps {
                sh '''
                syft dir:. -o spdx-json > sbom.spdx.json
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: '*.xml, *.json, *.spdx.json', fingerprint: true
            sh '''
            deactivate || true
            rm -rf venv
            '''
            cleanWs()
        }
    }
}
