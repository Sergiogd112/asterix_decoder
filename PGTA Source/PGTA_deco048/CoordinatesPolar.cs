using System;
using System.Text;

namespace PGTA_deco048;

public class CoordinatesPolar : Coordinates
{
	private double rho;

	private double theta;

	private double elevation;

	public double Rho
	{
		get
		{
			return rho;
		}
		set
		{
			rho = value;
		}
	}

	public double Theta
	{
		get
		{
			return theta;
		}
		set
		{
			theta = value;
		}
	}

	public double Elevation
	{
		get
		{
			return elevation;
		}
		set
		{
			elevation = value;
		}
	}

	public CoordinatesPolar()
	{
	}

	public CoordinatesPolar(double rho, double theta, double elevation)
	{
		Rho = rho;
		Theta = theta;
		Elevation = elevation;
	}

	public static string ToString(CoordinatesPolar c)
	{
		StringBuilder stringBuilder = new StringBuilder();
		stringBuilder.AppendFormat(" R: {0:f4}m T: {1:f4}rad E: {2:f4}rad", c.Rho, c.Theta, c.Elevation);
		return stringBuilder.ToString();
	}

	public static string ToStringStandard(CoordinatesPolar c)
	{
		StringBuilder stringBuilder = new StringBuilder();
		stringBuilder.AppendFormat(" R: {0:f4}NM T: {1:f4}º E: {2:f4}º", c.Rho * 0.0005399568034557236, c.Theta * (180.0 / Math.PI), c.Elevation * (180.0 / Math.PI));
		return stringBuilder.ToString();
	}
}
