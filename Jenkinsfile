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

        stage('Run Tests & Bandit') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    echo "Using pip from: $(which pip)"
                    unset PIP_REQUIRE_VIRTUALENV
                    pip install --upgrade pip --break-system-packages
                    pip install -r requirements.txt --break-system-packages
                    pip install bandit pytest --break-system-packages                    
                    pytest --maxfail=1 --disable-warnings --junitxml=report.xml
                    bandit -r . -f json -o bandit-report.json || true
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
    }

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
