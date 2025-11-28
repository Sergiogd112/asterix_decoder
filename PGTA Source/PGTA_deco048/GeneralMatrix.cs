using System;
using System.Runtime.Serialization;

namespace PGTA_deco048;

[Serializable]
public class GeneralMatrix : ICloneable, ISerializable, IDisposable
{
	private double[][] A;

	private int m;

	private int n;

	public virtual double[][] Array => A;

	public virtual double[][] ArrayCopy
	{
		get
		{
			double[][] array = new double[m][];
			for (int i = 0; i < m; i++)
			{
				array[i] = new double[n];
			}
			for (int j = 0; j < m; j++)
			{
				for (int k = 0; k < n; k++)
				{
					array[j][k] = A[j][k];
				}
			}
			return array;
		}
	}

	public virtual double[] ColumnPackedCopy
	{
		get
		{
			double[] array = new double[m * n];
			for (int i = 0; i < m; i++)
			{
				for (int j = 0; j < n; j++)
				{
					array[i + j * m] = A[i][j];
				}
			}
			return array;
		}
	}

	public virtual double[] RowPackedCopy
	{
		get
		{
			double[] array = new double[m * n];
			for (int i = 0; i < m; i++)
			{
				for (int j = 0; j < n; j++)
				{
					array[i * n + j] = A[i][j];
				}
			}
			return array;
		}
	}

	public virtual int RowDimension => m;

	public virtual int ColumnDimension => n;

	public GeneralMatrix(int m, int n)
	{
		this.m = m;
		this.n = n;
		A = new double[m][];
		for (int i = 0; i < m; i++)
		{
			A[i] = new double[n];
		}
	}

	public GeneralMatrix(int m, int n, double s)
	{
		this.m = m;
		this.n = n;
		A = new double[m][];
		for (int i = 0; i < m; i++)
		{
			A[i] = new double[n];
		}
		for (int j = 0; j < m; j++)
		{
			for (int k = 0; k < n; k++)
			{
				A[j][k] = s;
			}
		}
	}

	public GeneralMatrix(double[][] A)
	{
		m = A.Length;
		n = A[0].Length;
		for (int i = 0; i < m; i++)
		{
			if (A[i].Length != n)
			{
				throw new ArgumentException("All rows must have the same length.");
			}
		}
		this.A = A;
	}

	public GeneralMatrix(double[][] A, int m, int n)
	{
		this.A = A;
		this.m = m;
		this.n = n;
	}

	public GeneralMatrix(double[] vals, int m)
	{
		this.m = m;
		n = ((m != 0) ? (vals.Length / m) : 0);
		if (m * n != vals.Length)
		{
			throw new ArgumentException("Array length must be a multiple of m.");
		}
		A = new double[m][];
		for (int i = 0; i < m; i++)
		{
			A[i] = new double[n];
		}
		for (int j = 0; j < m; j++)
		{
			for (int k = 0; k < n; k++)
			{
				A[j][k] = vals[j + k * m];
			}
		}
	}

	public static GeneralMatrix Create(double[][] A)
	{
		int num = A.Length;
		int num2 = A[0].Length;
		GeneralMatrix generalMatrix = new GeneralMatrix(num, num2);
		double[][] array = generalMatrix.Array;
		for (int i = 0; i < num; i++)
		{
			if (A[i].Length != num2)
			{
				throw new ArgumentException("All rows must have the same length.");
			}
			for (int j = 0; j < num2; j++)
			{
				array[i][j] = A[i][j];
			}
		}
		return generalMatrix;
	}

	public virtual GeneralMatrix Copy()
	{
		GeneralMatrix generalMatrix = new GeneralMatrix(m, n);
		double[][] array = generalMatrix.Array;
		for (int i = 0; i < m; i++)
		{
			for (int j = 0; j < n; j++)
			{
				array[i][j] = A[i][j];
			}
		}
		return generalMatrix;
	}

	public virtual double GetElement(int i, int j)
	{
		return A[i][j];
	}

	public virtual GeneralMatrix GetMatrix(int i0, int i1, int j0, int j1)
	{
		GeneralMatrix generalMatrix = new GeneralMatrix(i1 - i0 + 1, j1 - j0 + 1);
		double[][] array = generalMatrix.Array;
		try
		{
			for (int k = i0; k <= i1; k++)
			{
				for (int l = j0; l <= j1; l++)
				{
					array[k - i0][l - j0] = A[k][l];
				}
			}
			return generalMatrix;
		}
		catch (IndexOutOfRangeException innerException)
		{
			throw new IndexOutOfRangeException("Submatrix indices", innerException);
		}
	}

	public virtual GeneralMatrix GetMatrix(int[] r, int[] c)
	{
		GeneralMatrix generalMatrix = new GeneralMatrix(r.Length, c.Length);
		double[][] array = generalMatrix.Array;
		try
		{
			for (int i = 0; i < r.Length; i++)
			{
				for (int j = 0; j < c.Length; j++)
				{
					array[i][j] = A[r[i]][c[j]];
				}
			}
			return generalMatrix;
		}
		catch (IndexOutOfRangeException innerException)
		{
			throw new IndexOutOfRangeException("Submatrix indices", innerException);
		}
	}

	public virtual GeneralMatrix GetMatrix(int i0, int i1, int[] c)
	{
		GeneralMatrix generalMatrix = new GeneralMatrix(i1 - i0 + 1, c.Length);
		double[][] array = generalMatrix.Array;
		try
		{
			for (int j = i0; j <= i1; j++)
			{
				for (int k = 0; k < c.Length; k++)
				{
					array[j - i0][k] = A[j][c[k]];
				}
			}
			return generalMatrix;
		}
		catch (IndexOutOfRangeException innerException)
		{
			throw new IndexOutOfRangeException("Submatrix indices", innerException);
		}
	}

	public virtual GeneralMatrix GetMatrix(int[] r, int j0, int j1)
	{
		GeneralMatrix generalMatrix = new GeneralMatrix(r.Length, j1 - j0 + 1);
		double[][] array = generalMatrix.Array;
		try
		{
			for (int i = 0; i < r.Length; i++)
			{
				for (int k = j0; k <= j1; k++)
				{
					array[i][k - j0] = A[r[i]][k];
				}
			}
			return generalMatrix;
		}
		catch (IndexOutOfRangeException innerException)
		{
			throw new IndexOutOfRangeException("Submatrix indices", innerException);
		}
	}

	public virtual void SetElement(int i, int j, double s)
	{
		A[i][j] = s;
	}

	public virtual void SetMatrix(int i0, int i1, int j0, int j1, GeneralMatrix X)
	{
		try
		{
			for (int k = i0; k <= i1; k++)
			{
				for (int l = j0; l <= j1; l++)
				{
					A[k][l] = X.GetElement(k - i0, l - j0);
				}
			}
		}
		catch (IndexOutOfRangeException innerException)
		{
			throw new IndexOutOfRangeException("Submatrix indices", innerException);
		}
	}

	public virtual void SetMatrix(int[] r, int[] c, GeneralMatrix X)
	{
		try
		{
			for (int i = 0; i < r.Length; i++)
			{
				for (int j = 0; j < c.Length; j++)
				{
					A[r[i]][c[j]] = X.GetElement(i, j);
				}
			}
		}
		catch (IndexOutOfRangeException innerException)
		{
			throw new IndexOutOfRangeException("Submatrix indices", innerException);
		}
	}

	public virtual void SetMatrix(int[] r, int j0, int j1, GeneralMatrix X)
	{
		try
		{
			for (int i = 0; i < r.Length; i++)
			{
				for (int k = j0; k <= j1; k++)
				{
					A[r[i]][k] = X.GetElement(i, k - j0);
				}
			}
		}
		catch (IndexOutOfRangeException innerException)
		{
			throw new IndexOutOfRangeException("Submatrix indices", innerException);
		}
	}

	public virtual void SetMatrix(int i0, int i1, int[] c, GeneralMatrix X)
	{
		try
		{
			for (int j = i0; j <= i1; j++)
			{
				for (int k = 0; k < c.Length; k++)
				{
					A[j][c[k]] = X.GetElement(j - i0, k);
				}
			}
		}
		catch (IndexOutOfRangeException innerException)
		{
			throw new IndexOutOfRangeException("Submatrix indices", innerException);
		}
	}

	public virtual GeneralMatrix Transpose()
	{
		GeneralMatrix generalMatrix = new GeneralMatrix(n, m);
		double[][] array = generalMatrix.Array;
		for (int i = 0; i < m; i++)
		{
			for (int j = 0; j < n; j++)
			{
				array[j][i] = A[i][j];
			}
		}
		return generalMatrix;
	}

	public virtual double Norm1()
	{
		double num = 0.0;
		for (int i = 0; i < n; i++)
		{
			double num2 = 0.0;
			for (int j = 0; j < m; j++)
			{
				num2 += Math.Abs(A[j][i]);
			}
			num = Math.Max(num, num2);
		}
		return num;
	}

	public virtual double NormInf()
	{
		double num = 0.0;
		for (int i = 0; i < m; i++)
		{
			double num2 = 0.0;
			for (int j = 0; j < n; j++)
			{
				num2 += Math.Abs(A[i][j]);
			}
			num = Math.Max(num, num2);
		}
		return num;
	}

	public virtual double NormF()
	{
		double num = 0.0;
		for (int i = 0; i < m; i++)
		{
			for (int j = 0; j < n; j++)
			{
				num = Maths.Hypot(num, A[i][j]);
			}
		}
		return num;
	}

	public virtual GeneralMatrix UnaryMinus()
	{
		GeneralMatrix generalMatrix = new GeneralMatrix(m, n);
		double[][] array = generalMatrix.Array;
		for (int i = 0; i < m; i++)
		{
			for (int j = 0; j < n; j++)
			{
				array[i][j] = 0.0 - A[i][j];
			}
		}
		return generalMatrix;
	}

	public virtual GeneralMatrix Add(GeneralMatrix B)
	{
		CheckMatrixDimensions(B);
		GeneralMatrix generalMatrix = new GeneralMatrix(m, n);
		double[][] array = generalMatrix.Array;
		for (int i = 0; i < m; i++)
		{
			for (int j = 0; j < n; j++)
			{
				array[i][j] = A[i][j] + B.A[i][j];
			}
		}
		return generalMatrix;
	}

	public virtual GeneralMatrix AddEquals(GeneralMatrix B)
	{
		CheckMatrixDimensions(B);
		for (int i = 0; i < m; i++)
		{
			for (int j = 0; j < n; j++)
			{
				A[i][j] = A[i][j] + B.A[i][j];
			}
		}
		return this;
	}

	public virtual GeneralMatrix Subtract(GeneralMatrix B)
	{
		CheckMatrixDimensions(B);
		GeneralMatrix generalMatrix = new GeneralMatrix(m, n);
		double[][] array = generalMatrix.Array;
		for (int i = 0; i < m; i++)
		{
			for (int j = 0; j < n; j++)
			{
				array[i][j] = A[i][j] - B.A[i][j];
			}
		}
		return generalMatrix;
	}

	public virtual GeneralMatrix SubtractEquals(GeneralMatrix B)
	{
		CheckMatrixDimensions(B);
		for (int i = 0; i < m; i++)
		{
			for (int j = 0; j < n; j++)
			{
				A[i][j] = A[i][j] - B.A[i][j];
			}
		}
		return this;
	}

	public virtual GeneralMatrix ArrayMultiply(GeneralMatrix B)
	{
		CheckMatrixDimensions(B);
		GeneralMatrix generalMatrix = new GeneralMatrix(m, n);
		double[][] array = generalMatrix.Array;
		for (int i = 0; i < m; i++)
		{
			for (int j = 0; j < n; j++)
			{
				array[i][j] = A[i][j] * B.A[i][j];
			}
		}
		return generalMatrix;
	}

	public virtual GeneralMatrix ArrayMultiplyEquals(GeneralMatrix B)
	{
		CheckMatrixDimensions(B);
		for (int i = 0; i < m; i++)
		{
			for (int j = 0; j < n; j++)
			{
				A[i][j] = A[i][j] * B.A[i][j];
			}
		}
		return this;
	}

	public virtual GeneralMatrix ArrayRightDivide(GeneralMatrix B)
	{
		CheckMatrixDimensions(B);
		GeneralMatrix generalMatrix = new GeneralMatrix(m, n);
		double[][] array = generalMatrix.Array;
		for (int i = 0; i < m; i++)
		{
			for (int j = 0; j < n; j++)
			{
				array[i][j] = A[i][j] / B.A[i][j];
			}
		}
		return generalMatrix;
	}

	public virtual GeneralMatrix ArrayRightDivideEquals(GeneralMatrix B)
	{
		CheckMatrixDimensions(B);
		for (int i = 0; i < m; i++)
		{
			for (int j = 0; j < n; j++)
			{
				A[i][j] = A[i][j] / B.A[i][j];
			}
		}
		return this;
	}

	public virtual GeneralMatrix ArrayLeftDivide(GeneralMatrix B)
	{
		CheckMatrixDimensions(B);
		GeneralMatrix generalMatrix = new GeneralMatrix(m, n);
		double[][] array = generalMatrix.Array;
		for (int i = 0; i < m; i++)
		{
			for (int j = 0; j < n; j++)
			{
				array[i][j] = B.A[i][j] / A[i][j];
			}
		}
		return generalMatrix;
	}

	public virtual GeneralMatrix ArrayLeftDivideEquals(GeneralMatrix B)
	{
		CheckMatrixDimensions(B);
		for (int i = 0; i < m; i++)
		{
			for (int j = 0; j < n; j++)
			{
				A[i][j] = B.A[i][j] / A[i][j];
			}
		}
		return this;
	}

	public virtual GeneralMatrix Multiply(double s)
	{
		GeneralMatrix generalMatrix = new GeneralMatrix(m, n);
		double[][] array = generalMatrix.Array;
		for (int i = 0; i < m; i++)
		{
			for (int j = 0; j < n; j++)
			{
				array[i][j] = s * A[i][j];
			}
		}
		return generalMatrix;
	}

	public virtual GeneralMatrix MultiplyEquals(double s)
	{
		for (int i = 0; i < m; i++)
		{
			for (int j = 0; j < n; j++)
			{
				A[i][j] = s * A[i][j];
			}
		}
		return this;
	}

	public virtual GeneralMatrix Multiply(GeneralMatrix B)
	{
		if (B.m != n)
		{
			throw new ArgumentException("GeneralMatrix inner dimensions must agree.");
		}
		GeneralMatrix generalMatrix = new GeneralMatrix(m, B.n);
		double[][] array = generalMatrix.Array;
		double[] array2 = new double[n];
		for (int i = 0; i < B.n; i++)
		{
			for (int j = 0; j < n; j++)
			{
				array2[j] = B.A[j][i];
			}
			for (int k = 0; k < m; k++)
			{
				double[] array3 = A[k];
				double num = 0.0;
				for (int l = 0; l < n; l++)
				{
					num += array3[l] * array2[l];
				}
				array[k][i] = num;
			}
		}
		return generalMatrix;
	}

	public static GeneralMatrix operator +(GeneralMatrix m1, GeneralMatrix m2)
	{
		return m1.Add(m2);
	}

	public static GeneralMatrix operator -(GeneralMatrix m1, GeneralMatrix m2)
	{
		return m1.Subtract(m2);
	}

	public static GeneralMatrix operator *(GeneralMatrix m1, GeneralMatrix m2)
	{
		return m1.Multiply(m2);
	}

	public virtual double Trace()
	{
		double num = 0.0;
		for (int i = 0; i < Math.Min(m, n); i++)
		{
			num += A[i][i];
		}
		return num;
	}

	public static GeneralMatrix Random(int m, int n)
	{
		Random random = new Random();
		GeneralMatrix generalMatrix = new GeneralMatrix(m, n);
		double[][] array = generalMatrix.Array;
		for (int i = 0; i < m; i++)
		{
			for (int j = 0; j < n; j++)
			{
				array[i][j] = random.NextDouble();
			}
		}
		return generalMatrix;
	}

	public static GeneralMatrix Identity(int m, int n)
	{
		GeneralMatrix generalMatrix = new GeneralMatrix(m, n);
		double[][] array = generalMatrix.Array;
		for (int i = 0; i < m; i++)
		{
			for (int j = 0; j < n; j++)
			{
				array[i][j] = ((i == j) ? 1.0 : 0.0);
			}
		}
		return generalMatrix;
	}

	private void CheckMatrixDimensions(GeneralMatrix B)
	{
		if (B.m != m || B.n != n)
		{
			throw new ArgumentException("GeneralMatrix dimensions must agree.");
		}
	}

	public void Dispose()
	{
		Dispose(disposing: true);
	}

	private void Dispose(bool disposing)
	{
		if (disposing)
		{
			GC.SuppressFinalize(this);
		}
	}

	~GeneralMatrix()
	{
		Dispose(disposing: false);
	}

	public object Clone()
	{
		return Copy();
	}

	void ISerializable.GetObjectData(SerializationInfo info, StreamingContext context)
	{
	}
}
