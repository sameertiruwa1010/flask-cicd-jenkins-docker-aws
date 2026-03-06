// Jenkins Declarative Pipeline
// CI/CD for Flask application using Docker and EC2

pipeline {

    // Run pipeline on any available Jenkins agent
    agent any

    // Global environment variables
    environment {
        APP_NAME       = "flask-ci-cd-demo"
        DOCKER_IMAGE   = "nyapu1010/flask-app"
        DOCKER_TAG     = "${BUILD_NUMBER}"
        STAGING_SERVER = "13.233.247.92"
    }

    stages {

        // -------------------------------
        // Checkout application source code
        // -------------------------------
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/sameertiruwa1010/flask-cicd-jenkins-docker-aws.git',
                    credentialsId: 'github-credentials'
            }
        }

        // ---------------------------------------
        // Install Python dependencies (optional)
        // Useful if tests or linting are added
        // ---------------------------------------
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

        // -------------------------------
        // Build Docker image
        // -------------------------------
        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image ${DOCKER_IMAGE}:${DOCKER_TAG}"
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                }
            }
        }

        // -----------------------------------
        // Push image to DockerHub registry
        // -----------------------------------
        stage('Push Docker Image') {
            steps {
                script {
                    docker.withRegistry('', 'dockerhub-credentials') {
                        def image = docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}")

                        image.push()
                        image.push('latest')
                    }
                }
            }
        }

        // -----------------------------------
        // Deploy latest image to EC2 server
        // -----------------------------------
        stage('Deploy to Staging') {
            steps {
                sshagent(['staging-server-ssh']) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ubuntu@${STAGING_SERVER} '
                            
                            echo "Pulling latest image..."
                            docker pull ${DOCKER_IMAGE}:latest

                            echo "Stopping existing container (if running)..."
                            docker stop ${APP_NAME} || true

                            echo "Removing old container..."
                            docker rm ${APP_NAME} || true

                            echo "Starting new container..."
                            docker run -d \
                                --name ${APP_NAME} \
                                --restart unless-stopped \
                                -p 5000:5000 \
                                -e FLASK_ENV=staging \
                                ${DOCKER_IMAGE}:latest

                            echo "Removing unused Docker images..."
                            docker image prune -f

                            echo "Current running containers:"
                            docker ps
                        '
                    """
                }
            }
        }

        // -----------------------------------
        // Verify application health endpoint
        // -----------------------------------
        stage('Health Check') {
            steps {
                sleep(10)

                sh """
                    echo "Checking application endpoint..."
                    curl -f http://${STAGING_SERVER}:5000/health
                """
            }
        }
    }

    // -----------------------------------
    // Post pipeline actions
    // -----------------------------------
    post {

        success {
            echo "Deployment successful"
            echo "Application URL: http://${STAGING_SERVER}:5000"
        }

        failure {
            echo "Pipeline failed. Check console logs."
        }

        always {
            // Clean Jenkins workspace
            cleanWs()
        }
    }
}
