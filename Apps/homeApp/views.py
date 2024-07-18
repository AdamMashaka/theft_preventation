import pickle
import pandas as pd
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import DataFileUpload
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score

# Load your model from the pickle file
with open('models3/fraud.pkl', 'rb') as model_file:
    loaded_model = pickle.load(model_file)
    
# Load the scaler used during training
with open('models3/scaler.pkl', 'rb') as scaler_file:
    scaler = pickle.load(scaler_file)

def base(request):
    return render(request, 'homeApp/landing_page.html')

def upload_credit_data(request):
    return render(request, 'homeApp/upload_credit_data.html')

def reports(request):
    all_data_files_objs = DataFileUpload.objects.all()
    return render(request, 'homeApp/reports.html', {'all_files': all_data_files_objs})

def account_details(request):
    return render(request, 'homeApp/account_details.html')

def change_password(request):
    return render(request, 'homeApp/change_password.html')

def analysis(request, id):
    target_column = 'target_column_name'
    obj = DataFileUpload.objects.get(id=id)
    df = pd.read_csv(obj.actual_file.path)

    # Make predictions using the loaded model
    predictions = loaded_model.predict(df)
    
    # Calculate statistics
    empty_columns = len(df.columns[df.isnull().all()].tolist())
    data_shape = df.shape
    unique_targets = df[['online_order', 'distance_from_home']].drop_duplicates().values.tolist()

    percent_no_problem = 100 * (predictions == 0).sum() / len(predictions)
    percent_problem = 100 * (predictions == 1).sum() / len(predictions)
    num_fraud_transactions = (predictions == 1).sum()
    has_null = df.isnull().any().any()
    fraud_shape = (num_fraud_transactions, df.shape[1])
    normal_shape = ((predictions == 0).sum(), df.shape[1])

    context = {
        'data_shape': data_shape,
        'empty_columns': empty_columns,
        'unique_targets': unique_targets,
        'percent_no_problem': round(percent_no_problem, 3),
        'percent_problem': round(percent_problem, 3),
        'num_fraud_transactions': num_fraud_transactions,
        'has_null': has_null,
        'fraud_shape': fraud_shape,
        'normal_shape': normal_shape
    }

    return render(request, 'homeApp/analysis.html', context)

def view_data(request, id):
    obj = DataFileUpload.objects.get(id=id)
    df = pd.read_csv(obj.actual_file.path)
    columns = df.columns.tolist()
    data = df.head(10).to_dict(orient='records')  # Displaying the first 10 rows for view
    return render(request, 'homeApp/view_data.html', {'id': id, 'columns': columns, 'data': data})

def delete_data(request, id):
    obj = DataFileUpload.objects.get(id=id)
    obj.delete()
    messages.success(request, "File Deleted successfully", extra_tags='alert alert-success alert-dismissible show')
    return HttpResponseRedirect('/reports')

def upload_data(request):
    if request.method == 'POST':
        data_file_name = request.POST.get('data_file_name')
        try:
            actual_file = request.FILES['actual_file_name']
            data = pd.read_csv(actual_file)
            
            # Assuming last column is the target variable and others are features
            X = data.iloc[:, :-1].values
            y = data.iloc[:, -1].values
            
            # Splitting the dataset into training and test sets
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
            
            # Feature scaling
            sc = StandardScaler()
            X_train = sc.fit_transform(X_train)
            X_test = sc.transform(X_test)
            
            # Train the logistic regression model
            classifier = LogisticRegression(random_state=0)
            classifier.fit(X_train, y_train)
            
            # Serialize the model
            serialized_model = pickle.dumps(classifier)
            serialized_x_test = pickle.dumps(X_test)
            serialized_y_test = pickle.dumps(y_test)
            
            description = request.POST.get('description')

            DataFileUpload.objects.create(
                file_name=data_file_name,
                actual_file=actual_file,
                description=description,
                trained_model_data=serialized_model,
                x_test_data=serialized_x_test,
                y_test_data=serialized_y_test
            )
            
            messages.success(request, "File Uploaded successfully", extra_tags='alert alert-success alert-dismissible show')
            return HttpResponseRedirect('/reports')
            
        except:
            messages.warning(request, "Invalid/wrong format. Please upload File.")
            return redirect('/upload_credit_data')

def retrieve_data_by_id(request, id):
    obj = DataFileUpload.objects.get(id=id)
    df = pd.read_csv(obj.actual_file.path)

    # Receive parameters from DataTables on the frontend
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    
    # Paginate the data from the CSV using start and length
    paginated_df = df.iloc[start:start+length].reset_index()
    paginated_df['index'] = paginated_df['index'] + 1 + start

    # Convert the paginated data to a list of lists
    data = paginated_df.values.tolist()

    # Return a JSON response suitable for DataTables
    return JsonResponse({
        'draw': draw,
        'recordsTotal': len(df),
        'recordsFiltered': len(df),  # In case you add server-side filtering later on
        'data': data,
    })

def userLogout(request):
    try:
        del request.session['username']
    except:
        pass
    logout(request)
    return HttpResponseRedirect('/')

def login2(request):
    data = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            data['error'] = "Username or Password is incorrect"
            return render(request, 'homeApp/login.html', data)
    else:
        return render(request, 'homeApp/login.html', data)

def about(request):
    return render(request, 'homeApp/about.html')

def dashboard(request):
    return render(request, 'homeApp/dashboard.html')
