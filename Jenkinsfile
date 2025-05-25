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

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv("${SONARQUBE_ENV}") {
                    withCredentials([string(credentialsId: 'sonarqube-token', variable: 'SONAR_TOKEN')]) {
                        sh 'sonar-scanner -Dsonar.login=$SONAR_TOKEN'
                    }
                }
            }
        }
    }  // <-- closing stages block here

    post {
        always {
            echo "🧹 Cleaning up workspace..."
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
