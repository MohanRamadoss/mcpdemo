#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_status "🛠️ Setting up EKS Prerequisites"

# Function to install AWS CLI
install_aws_cli() {
    print_status "Installing AWS CLI v2..."
    
    if command -v aws &> /dev/null; then
        print_success "AWS CLI already installed"
        aws --version
        return 0
    fi
    
    # Install AWS CLI v2
    case "$(uname -s)" in
        Linux*)
            curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
            unzip awscliv2.zip
            sudo ./aws/install
            rm -rf awscliv2.zip aws/
            ;;
        Darwin*)
            curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
            sudo installer -pkg AWSCLIV2.pkg -target /
            rm AWSCLIV2.pkg
            ;;
        *)
            print_error "Unsupported OS: $(uname -s)"
            exit 1
            ;;
    esac
    
    print_success "AWS CLI installed successfully"
}

# Function to install eksctl
install_eksctl() {
    print_status "Installing eksctl..."
    
    if command -v eksctl &> /dev/null; then
        print_success "eksctl already installed"
        eksctl version
        return 0
    fi
    
    # Install eksctl
    case "$(uname -s)" in
        Linux*)
            ARCH=amd64
            PLATFORM=$(uname -s)_$ARCH
            
            curl -sLO "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_$PLATFORM.tar.gz"
            tar -xzf "eksctl_$PLATFORM.tar.gz" -C /tmp && rm "eksctl_$PLATFORM.tar.gz"
            sudo mv /tmp/eksctl /usr/local/bin
            ;;
        Darwin*)
            # Install via Homebrew if available, otherwise direct download
            if command -v brew &> /dev/null; then
                brew tap weaveworks/tap
                brew install weaveworks/tap/eksctl
            else
                ARCH=amd64
                PLATFORM=$(uname -s)_$ARCH
                
                curl -sLO "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_$PLATFORM.tar.gz"
                tar -xzf "eksctl_$PLATFORM.tar.gz" -C /tmp && rm "eksctl_$PLATFORM.tar.gz"
                sudo mv /tmp/eksctl /usr/local/bin
            fi
            ;;
        *)
            print_error "Unsupported OS: $(uname -s)"
            exit 1
            ;;
    esac
    
    print_success "eksctl installed successfully"
}

# Function to install kubectl
install_kubectl() {
    print_status "Installing kubectl..."
    
    if command -v kubectl &> /dev/null; then
        print_success "kubectl already installed"
        kubectl version --client
        return 0
    fi
    
    # Install kubectl
    case "$(uname -s)" in
        Linux*)
            curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
            chmod +x kubectl
            sudo mv kubectl /usr/local/bin/
            ;;
        Darwin*)
            if command -v brew &> /dev/null; then
                brew install kubectl
            else
                curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/amd64/kubectl"
                chmod +x kubectl
                sudo mv kubectl /usr/local/bin/
            fi
            ;;
        *)
            print_error "Unsupported OS: $(uname -s)"
            exit 1
            ;;
    esac
    
    print_success "kubectl installed successfully"
}

# Function to install Helm
install_helm() {
    print_status "Installing Helm..."
    
    if command -v helm &> /dev/null; then
        print_success "Helm already installed"
        helm version
        return 0
    fi
    
    # Install Helm
    case "$(uname -s)" in
        Linux*)
            curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
            ;;
        Darwin*)
            if command -v brew &> /dev/null; then
                brew install helm
            else
                curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
            fi
            ;;
        *)
            print_error "Unsupported OS: $(uname -s)"
            exit 1
            ;;
    esac
    
    print_success "Helm installed successfully"
}

# Function to install Go (for kubectl-ai)
install_go() {
    print_status "Installing Go..."
    
    if command -v go &> /dev/null; then
        print_success "Go already installed"
        go version
        return 0
    fi
    
    # Install Go
    case "$(uname -s)" in
        Linux*)
            GO_VERSION="1.22.3"
            wget "https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz"
            sudo tar -C /usr/local -xzf "go${GO_VERSION}.linux-amd64.tar.gz"
            rm "go${GO_VERSION}.linux-amd64.tar.gz"
            
            # Add to PATH
            echo 'export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin' >> ~/.bashrc
            export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin
            ;;
        Darwin*)
            if command -v brew &> /dev/null; then
                brew install go
            else
                GO_VERSION="1.22.3"
                curl -LO "https://go.dev/dl/go${GO_VERSION}.darwin-amd64.tar.gz"
                sudo tar -C /usr/local -xzf "go${GO_VERSION}.darwin-amd64.tar.gz"
                rm "go${GO_VERSION}.darwin-amd64.tar.gz"
                
                # Add to PATH
                echo 'export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin' >> ~/.zshrc
                export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin
            fi
            ;;
        *)
            print_error "Unsupported OS: $(uname -s)"
            exit 1
            ;;
    esac
    
    print_success "Go installed successfully"
}

# Function to configure AWS credentials
configure_aws() {
    print_status "Checking AWS credentials..."
    
    if aws sts get-caller-identity &> /dev/null; then
        print_success "AWS credentials already configured"
        aws sts get-caller-identity
        return 0
    fi
    
    print_warning "AWS credentials not configured"
    echo "Please run 'aws configure' to set up your credentials"
    echo "You'll need:"
    echo "- AWS Access Key ID"
    echo "- AWS Secret Access Key"
    echo "- Default region (e.g., us-east-1)"
    echo "- Default output format (json)"
    
    read -p "Do you want to configure AWS credentials now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        aws configure
        
        if aws sts get-caller-identity &> /dev/null; then
            print_success "AWS credentials configured successfully"
        else
            print_error "Failed to configure AWS credentials"
            exit 1
        fi
    else
        print_warning "Skipping AWS credentials configuration"
        print_warning "You'll need to configure them before deploying to EKS"
    fi
}

# Function to verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    local tools=("aws" "eksctl" "kubectl" "helm" "go")
    local failed=0
    
    for tool in "${tools[@]}"; do
        if command -v "$tool" &> /dev/null; then
            print_success "$tool is installed"
        else
            print_error "$tool is not installed"
            failed=1
        fi
    done
    
    if [ $failed -eq 0 ]; then
        print_success "All tools installed successfully!"
        return 0
    else
        print_error "Some tools failed to install"
        return 1
    fi
}

# Function to show next steps
show_next_steps() {
    echo
    echo "================================================"
    print_success "🎉 EKS Prerequisites Setup Complete!"
    echo "================================================"
    echo
    echo "📋 Installed Tools:"
    echo "• AWS CLI v2"
    echo "• eksctl"
    echo "• kubectl"
    echo "• Helm"
    echo "• Go (for kubectl-ai)"
    echo
    echo "🚀 Next Steps:"
    echo "1. Configure AWS credentials (if not done already):"
    echo "   aws configure"
    echo
    echo "2. Deploy EKS cluster:"
    echo "   ./deploy-eks.sh"
    echo
    echo "3. Or follow the manual deployment guide in README.md"
    echo
    echo "💡 Useful Commands:"
    echo "• aws sts get-caller-identity    # Verify AWS credentials"
    echo "• eksctl get clusters            # List EKS clusters"
    echo "• kubectl get nodes              # List cluster nodes"
    echo "• helm list                      # List Helm releases"
    echo
    print_success "✅ Ready to deploy to EKS!"
}

# Main execution
main() {
    case "${1:-all}" in
        "all")
            install_aws_cli
            install_eksctl
            install_kubectl
            install_helm
            install_go
            configure_aws
            verify_installation
            show_next_steps
            ;;
        "aws")
            install_aws_cli
            configure_aws
            ;;
        "eksctl")
            install_eksctl
            ;;
        "kubectl")
            install_kubectl
            ;;
        "helm")
            install_helm
            ;;
        "go")
            install_go
            ;;
        "verify")
            verify_installation
            ;;
        "help"|"-h"|"--help")
            echo "Usage: $0 [all|aws|eksctl|kubectl|helm|go|verify|help]"
            echo
            echo "Commands:"
            echo "  all      - Install all prerequisites (default)"
            echo "  aws      - Install and configure AWS CLI"
            echo "  eksctl   - Install eksctl"
            echo "  kubectl  - Install kubectl"
            echo "  helm     - Install Helm"
            echo "  go       - Install Go"
            echo "  verify   - Verify all installations"
            echo "  help     - Show this help message"
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Execute main function
main "$@"
