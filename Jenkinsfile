// Jenkins Declarative Pipeline for LOCAL Jenkins
pipeline {

    // Run on local machine (no agent needed)
    agent any
    
    environment {
        APP_NAME = 'flask-ci-cd-demo'
        DOCKER_IMAGE = 'nyapu1010/flask-app'
        DOCKER_TAG = "${BUILD_NUMBER}"
        STAGING_SERVER = '13.233.247.92'
    }
    
    stages {
        stage('Checkout Code') {
            steps {
                // For local Jenkins, you can use:
                // Option 1: Clone from GitHub
                git branch: 'main', 
                    url: 'https://github.com/sameertiruwa1010/flask-cicd-jenkins-docker-aws.git',
                    credentialsId: 'github-credentials'
                
                // Option 2: Use local directory (simpler for testing)
                // dir('/path/to/your/local/project') {
                //     echo 'Using local project files'
                // }
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    // Build locally
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                }
            }
        }
        
        stage('Push to DockerHub') {
            steps {
                script {
                    docker.withRegistry('', 'dockerhub-credentials') {
                        docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}").push()
                        docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}").push('latest')
                    }
                }
            }
        }
        
        stage('Deploy to EC2 Staging') {
            steps {
                sshagent(['staging-server-ssh']) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ubuntu@${STAGING_SERVER} '
                            # Pull the latest image
                            docker pull ${DOCKER_IMAGE}:latest
                            
                            # Stop and remove old container
                            docker stop ${APP_NAME} || true
                            docker rm ${APP_NAME} || true
                            
                            # Run new container
                            docker run -d \\
                                --name ${APP_NAME} \\
                                --restart unless-stopped \\
                                -p 5000:5000 \\
                                -e FLASK_ENV=staging \\
                                ${DOCKER_IMAGE}:latest
                            
                            # Clean up old images
                            docker image prune -f
                            
                            # Show running containers
                            docker ps | grep ${APP_NAME}
                        '
                    """
                }
            }
        }
        
        stage('Health Check') {
            steps {
                sleep(10)
                sh """
                    curl -f http://${STAGING_SERVER}:5000/health || exit 1
                """
            }
        }
    }
    
    post {
        success {
            echo "✅ Pipeline Successful!"
            echo "App running at: http://${STAGING_SERVER}:5000"
        }
        failure {
            echo "❌ Pipeline Failed!"
        }
        always {
            cleanWs()
        }
    }
}
