namespace PGTA_deco048;

public class CoordinatesUVH : Coordinates
{
	private double u;

	private double v;

	private double h;

	public double U
	{
		get
		{
			return u;
		}
		set
		{
			u = value;
		}
	}

	public double V
	{
		get
		{
			return v;
		}
		set
		{
			v = value;
		}
	}

	public double Height
	{
		get
		{
			return h;
		}
		set
		{
			h = value;
		}
	}
}
