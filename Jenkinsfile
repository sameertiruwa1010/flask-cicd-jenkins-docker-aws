// Jenkins Declarative Pipeline
pipeline {

    // Run this pipeline on any available Jenkins agent/node
    agent any
    
    // Global environment variables used in the pipeline
    environment {

        // Name of the application/container
        APP_NAME = 'flask-ci-cd-demo'

        // Docker image repository (DockerHub username/image-name)
        DOCKER_IMAGE = 'nyapu1010/flask-app'

        // Use Jenkins build number as Docker image tag
        DOCKER_TAG = "${BUILD_NUMBER}"
        
        // IP address of staging server where the app will be deployed
        STAGING_SERVER = '13.201.117.15'
        
        // Jenkins stored credentials for DockerHub login
        DOCKER_CREDENTIALS = credentials('dockerhub-credentials')
    }
    
    stages {

        // -----------------------------
        // Stage 1: Get code from GitHub
        // -----------------------------
        stage('Checkout Code') {
            steps {

                // Clone the project repository from GitHub
                git branch: 'main', 
                    url: 'https://github.com/sameertiruwa1010/flask-cicd-jenkins-docker-aws.git',
                    credentialsId: 'github-credentials'
            }
        }
        
        // ------------------------------------
        // Stage 2: Create Python virtual env
        // and install project dependencies
        // ------------------------------------
        stage('Setup Python Environment') {
            steps {
                sh '''
                    # Create Python virtual environment
                    python3 -m venv venv

                    # Activate virtual environment
                    . venv/bin/activate

                    # Upgrade pip
                    pip install --upgrade pip

                    # Install required dependencies
                    pip install -r requirements.txt
                '''
            }
        }
        
        // -----------------------------
        // Stage 3: Run automated tests
        // -----------------------------
        stage('Run Tests') {
            steps {
                sh '''
                    # Activate Python environment
                    . venv/bin/activate

                    # Run unit tests using pytest
                    pytest tests/ -v --junitxml=test-results.xml
                '''
            }

            // Always publish test results even if tests fail
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }
        
        // -----------------------------
        // Stage 4: Code quality check
        // -----------------------------
        stage('Lint Code') {
            steps {
                sh '''
                    # Activate virtual environment
                    . venv/bin/activate

                    # Install pylint for static code analysis
                    pip install pylint

                    # Run lint check on main application file
                    # --exit-zero prevents pipeline failure for warnings
                    pylint app.py --exit-zero
                '''
            }
        }
        
        // -----------------------------
        // Stage 5: Build Docker Image
        // -----------------------------
        stage('Build Docker Image') {
            steps {
                script {

                    // Build Docker image with build number tag
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                }
            }
        }
        
        // ------------------------------------
        // Stage 6: Push Docker image to DockerHub
        // ------------------------------------
        stage('Push to DockerHub') {
            steps {
                script {

                    // Authenticate to DockerHub using Jenkins credentials
                    docker.withRegistry('', 'dockerhub-credentials') {

                        // Push versioned image
                        docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}").push()

                        // Also push image with 'latest' tag
                        docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}").push('latest')
                    }
                }
            }
        }
        
        // ------------------------------------
        // Stage 7: Deploy application to staging server
        // ------------------------------------
        stage('Deploy to Staging') {
            steps {

                // Use Jenkins SSH credentials to access remote server
                sshagent(['staging-server-ssh']) {

                    sh """
                        ssh -o StrictHostKeyChecking=no ubuntu@${STAGING_SERVER} '

                            # Pull the newest Docker image
                            docker pull ${DOCKER_IMAGE}:latest
                            
                            # Stop old container if running
                            docker stop ${APP_NAME} || true
                            
                            # Remove old container
                            docker rm ${APP_NAME} || true
                            
                            # Run new container with required configuration
                            docker run -d \\
                                --name ${APP_NAME} \\
                                --restart unless-stopped \\
                                -p 5000:5000 \\
                                -e FLASK_ENV=staging \\
                                --log-opt max-size=10m \\
                                --log-opt max-file=3 \\
                                ${DOCKER_IMAGE}:latest
                            
                            # Remove unused old Docker images
                            docker image prune -f
                            
                            # Verify container is running
                            docker ps | grep ${APP_NAME}
                        '
                    """
                }
            }
        }
        
        // -----------------------------
        // Stage 8: Application health check
        // -----------------------------
        stage('Health Check') {
            steps {

                // Wait few seconds for container startup
                sleep(10)

                sh """
                    # Check if application responds successfully
                    curl -f http://${STAGING_SERVER}:5000/health || exit 1
                """
            }
        }
    }
    
    // ------------------------------------
    // Post pipeline actions
    // ------------------------------------
    post {

        // If pipeline succeeds
        success {
            echo 'Pipeline completed successfully!'

            // Send success email notification
            emailext (
                to: 'sameertiruwa1010@gmail.com',
                subject: "Pipeline Success: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: "The pipeline has completed successfully.\nApp is running at: http://${STAGING_SERVER}:5000"
            )
        }

        // If pipeline fails
        failure {
            echo 'Pipeline failed!'

            // Send failure notification email
            emailext (
                to: 'sameertiruwa1010@gmail.com',
                subject: "Pipeline Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: "Please check the console output at: ${env.BUILD_URL}"
            )
        }

        // Always run this step
        always {

            // Clean Jenkins workspace after build
            cleanWs()
        }
    }
}
