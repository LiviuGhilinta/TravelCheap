pipeline{
    agent any
    
    stages{
        stage('Build'){
            steps{
                echo "Building project ..."

                sh '''

                python3 -m venv venv

                . venv/bin/activate

                python3 --version

                python3 -m pip install --upgrade pip
                
                pip install -r requirements.txt

                echo "Everything is installed. Next Step: Test"

                '''
            }
        }

        stage('Test'){
            steps{
                sh '''
                . venv/bin/activate
            
                pip install pytest

                pytest

                echo "Tests Passed! Moving to next step "
                '''
            }
        }

        stage('Deploy'){
            steps{
                sh''' 
                docker build -t travelcheap:${BUILD_NUMBER} -t travelcheap:latest .
                '''
            }
        }
    }
    
    post{
        always{
            sh 'rm -rf venv'
        }
    }
}