pipeline {
  agent {
    docker {
      image 'python:3.11-slim'
      args '--user root -v /var/run/docker.sock:/var/run/docker.sock'
    }
  }

  environment {
    APP_NAME = 'shopflow'
    IMAGE_TAG = 'latest'
  }

  stages {
    stage('Install') {
      steps {
        sh '''
          python -m pip install --upgrade pip
          pip install -r requirements.txt
        '''
      }
    }

    stage('Lint') {
      steps {
        sh 'python -m flake8 app'
      }
    }

    stage('Unit Tests') {
      steps {
        sh '''
          python -m pytest tests/unit -v -m "not integration" --junitxml=junit-unit.xml --no-cov
        '''
      }
      post {
        always {
          junit 'junit-unit.xml'
        }
      }
    }

    stage('Integration Tests') {
      steps {
        sh '''
          python -m pytest tests/integration -v --junitxml=junit-integration.xml --no-cov
        '''
      }
      post {
        always {
          junit 'junit-integration.xml'
        }
      }
    }

    stage('Coverage') {
      steps {
        sh '''
          python -m pytest tests --cov=app --cov-report=xml:coverage.xml --cov-report=html:htmlcov --cov-report=term-missing --cov-fail-under=80 --junitxml=junit-report.xml
        '''
      }
      post {
        always {
          publishHTML(target: [
            allowMissing: true,
            alwaysLinkToLastBuild: true,
            keepAll: true,
            reportDir: 'htmlcov',
            reportFiles: 'index.html',
            reportName: 'Coverage Report'
          ])
          junit 'junit-report.xml'
        }
      }
    }

    stage('Static Analysis') {
      steps {
        sh '''
          python -m pylint app --output-format=parseable --exit-zero > pylint-report.txt || true
          python -m bandit -r app -f json -o bandit-report.json --exit-zero
          python - <<'PY'
import json
import sys

with open('bandit-report.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
high = [r for r in data.get('results', []) if r.get('issue_severity') == 'HIGH']
if high:
    print(f'BANDIT: {len(high)} vuln HIGH detectee(s)')
    sys.exit(1)
print('BANDIT: aucune vulnerabilite HIGH')
PY
        '''
      }
    }

    stage('SonarQube Analysis') {
      steps {
        withSonarQubeEnv('SonarQube') {
          sh '''
            sonar-scanner -Dsonar.projectKey=shopflow -Dsonar.sources=app -Dsonar.tests=tests -Dsonar.python.coverage.reportPaths=coverage.xml -Dsonar.python.pylint.reportPaths=pylint-report.txt
          '''
        }
      }
    }

    stage('Quality Gate') {
      steps {
        timeout(time: 10, unit: 'MINUTES') {
          waitForQualityGate abortPipeline: true
        }
      }
    }

    stage('Build Docker') {
      steps {
        script {
          IMAGE_TAG = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
          sh "docker build -t shopflow:${IMAGE_TAG} ."
        }
      }
    }

    stage('Deploy Staging') {
      when {
        branch 'main'
      }
      steps {
        sh '''
          export IMAGE_TAG=${IMAGE_TAG}
          docker compose -f docker-compose.staging.yml pull || true
          docker compose -f docker-compose.staging.yml up -d --remove-orphans
          docker compose -f docker-compose.staging.yml ps
          sleep 5
          curl -f http://localhost:8001/health
        '''
      }
      post {
        failure {
          sh 'docker compose -f docker-compose.staging.yml logs --tail=50 || true'
        }
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: 'junit-*.xml,coverage.xml,bandit-report.json,pylint-report.txt', allowEmptyArchive: true
      echo 'Pipeline termine'
    }
    success {
      echo "Pipeline OK - ShopFlow:${IMAGE_TAG}"
    }
    failure {
      echo 'Pipeline FAILED'
    }
    unstable {
      echo 'Pipeline instable'
    }
  }
}
