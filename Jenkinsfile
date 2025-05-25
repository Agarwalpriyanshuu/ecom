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

        stage('Run Pytest') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    curl -sS https://bootstrap.pypa.io/get-pip.py | python3
                    pip install -r requirements.txt
                    pytest --maxfail=1 --disable-warnings --junitxml=report.xml
                '''
            }
        }

        stage('Run Bandit SAST') {
            steps {
                sh '''
                    . venv/bin/activate
                    pip install bandit
                    bandit -r . -f xml -o bandit-report.xml -lll
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv("${SONARQUBE_ENV}") {
                    withCredentials([string(credentialsId: 'sonarqube-token', variable: 'SONAR_TOKEN')]) {
                        sh 'sonar-scanner -Dsonar.login=$SONAR_TOKEN'
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 1, unit: 'MINUTES') {
                    waitForQualityGate(abortPipeline: true)
                }
            }
        }
    }

    post {
        always {
            echo "🧹 Cleaning up workspace..."
            // Publish Bandit report to Jenkins UI (requires Warnings Next Generation Plugin)
            recordIssues(tools: [bandit(pattern: 'bandit-report.xml')])
            deleteDir()
        }
        success {
            echo "✅ Build and tests passed successfully!"
        }
        failure {
            echo "❌ Build failed. Please check the logs above."
        }
    }
}
