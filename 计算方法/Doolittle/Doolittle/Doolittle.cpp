/*#include<iostream>
using namespace std;
int n;
double a[100][100], b[100], l[100][100], u[100][100], y[100], x[100];
void input() {
	for (int i = 0; i < n; i++) {
		for (int j = 0; j < n; j++)
			cin >> a[i][j];
			cin >> b[i];
	}
}

void Doolitte() {
	for (int i = 0; i < n; i++) {
		for (int j = 0; j < n; j++) {
			l[i][i] = 1;
			if (j > i) l[i][j] = 0;
			if (j < i) u[i][j] = 0;
		}
	}
	for (int k = 0; k < n; k++) {
		for (int j = k; j < n; j++) {
			u[k][j] = a[k][j];
			for (int i = 0; i <= k - 1; i++)
				u[k][j] -= (l[k][i] * u[i][j]);
		}
		for (int i = k + 1; i < n; i++) {
			l[i][k] = a[i][k];
			for (int j = 0; j <= k - 1; j++)
				l[i][k] -= (l[i][j] * u[j][k]);
			l[i][k] /= u[k][k];
		}
	}
	for (int i = 0; i < n; i++) {
		y[i] = b[i];
		for (int j = 0; j < i - 1; j++)
			y[i] -= (l[i][j] * y[j]);
	}

	for (int i = n - 1; i >= 0; i--) {
		x[i] = y[i];
		for (int j = i + 1; j < n; j++)
			x[i] -= (u[i][j] * x[j]);
		x[i] /= u[i][i];
	}
}


int main() {
	cout << "please input the rows/columns of the matrix:" << endl;
	cin >> n;
	cout << "please input the numbers of the matrix:";
	input();
	Doolitte();
	for (int i = 0; i < n; i++)
		cout << x[i] << " ";
	cout << endl;
	return 0;
}*/
#include<iostream>
using namespace std;

int n;
double a[100][100], b[100], l[100][100], u[100][100], y[100], x[100];

void input() {
	for (int i = 0; i < n; i++)
	{
		for (int j = 0; j < n; j++)
			cin >> a[i][j];
		    cin >> b[i];
	}
}

void Doolitte()
{
	for (int i = 0; i < n; i++)
	{
		for (int j = 0; j < n; j++)
		{
			l[i][i] = 1;
			if (j > i) l[i][j] = 0;
			if (j < i) u[i][j] = 0;
		}
	}
	for (int k = 0; k < n; k++) {
		for (int j = k; j < n; j++) {           // dolittle分解
			u[k][j] = a[k][j];
			for (int i = 0; i <= k - 1; i++)
				u[k][j] -= (l[k][i] * u[i][j]);
		}
		for (int i = k + 1; i < n; i++) {
			l[i][k] = a[i][k];
			for (int j = 0; j <= k - 1; j++)
				l[i][k] -= (l[i][j] * u[j][k]);
			l[i][k] /= u[k][k];
		}
	}

	for (int i = 0; i < n; i++) { // 解Ly = b
		y[i] = b[i];
		for (int j = 0; j <= i - 1; j++)
			y[i] -= (l[i][j] * y[j]);
	}

	for (int i = n - 1; i >= 0; i--) { // 解UX = Y
		x[i] = y[i];
		for (int j = i + 1; j < n; j++)
			x[i] -= (u[i][j] * x[j]);
		x[i] /= u[i][i];
	}
}

int main()
{
	cout << "输入系数矩阵的阶数" << endl;
	cin >> n;
	cout << "输入系数矩阵" << endl;
	input();
	Doolitte();
	for (int i = 0; i < n; i++)
		cout << x[i] << " ";
	cout << endl;
	return 0;
}

