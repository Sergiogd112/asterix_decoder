using System;

namespace PGTA_deco048;

internal class Maths
{
	public static double Hypot(double a, double b)
	{
		if (Math.Abs(a) > Math.Abs(b))
		{
			double num = b / a;
			return Math.Abs(a) * Math.Sqrt(1.0 + num * num);
		}
		if (b != 0.0)
		{
			double num = a / b;
			return Math.Abs(b) * Math.Sqrt(1.0 + num * num);
		}
		return 0.0;
	}
}
