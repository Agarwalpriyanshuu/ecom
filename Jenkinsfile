pipeline {
    agent any

    stages {
        stage('Install Dependencies and Run Tests') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    echo "Using pip from: $(which pip)"
                    unset PIP_REQUIRE_VIRTUALENV
                    pip install --upgrade pip --break-system-packages
                    pip install -r requirements.txt --break-system-packages

                    echo "Running tests..."
                    pytest --maxfail=1 --disable-warnings --junitxml=report.xml
                '''
            }
        }

        stage('Archive Reports') {
            steps {
                junit 'report.xml'
            }
        }
    }
}
