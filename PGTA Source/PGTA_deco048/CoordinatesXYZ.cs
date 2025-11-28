using System.Text;

namespace PGTA_deco048;

public class CoordinatesXYZ : Coordinates
{
	private double x;

	private double y;

	private double z;

	public double X
	{
		get
		{
			return x;
		}
		set
		{
			x = value;
		}
	}

	public double Y
	{
		get
		{
			return y;
		}
		set
		{
			y = value;
		}
	}

	public double Z
	{
		get
		{
			return z;
		}
		set
		{
			z = value;
		}
	}

	public CoordinatesXYZ()
	{
	}

	public CoordinatesXYZ(double x, double y, double z)
	{
		X = x;
		Y = y;
		Z = z;
	}

	public static string ToString(CoordinatesXYZ c)
	{
		StringBuilder stringBuilder = new StringBuilder();
		stringBuilder.AppendFormat(" X: {0:f4}m Y: {1:f4}m Z: {2:f4}m", c.X, c.Y, c.Z);
		return stringBuilder.ToString();
	}

	public override string ToString()
	{
		StringBuilder stringBuilder = new StringBuilder();
		stringBuilder.AppendFormat(" X: {0:f4}m Y: {1:f4}m Z: {2:f4}m", X, Y, Z);
		return stringBuilder.ToString();
	}
}
