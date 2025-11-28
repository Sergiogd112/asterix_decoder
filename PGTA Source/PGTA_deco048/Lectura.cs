using System;
using System.Collections.Generic;
using System.IO;

namespace PGTA_deco048;

public class Lectura
{
	private List<string> TI = new List<string>();

	private List<string> QNH = new List<string>();

	private List<string> TI_21 = new List<string>();

	private List<string> QNH_21 = new List<string>();

	public int bloques { get; set; }

	public int num21 { get; set; }

	public int num48 { get; set; }

	public List<Cat_048> Lista_cat48 { get; set; }

	public List<Cat_021> Lista_cat21 { get; set; }

	public List<Cat_ASTERIX> Lista_ASTERIX { get; set; }

	public Lectura(string path)
	{
		Lista_cat48 = new List<Cat_048>();
		Lista_cat21 = new List<Cat_021>();
		Lista_ASTERIX = new List<Cat_ASTERIX>();
		bloques = 0;
		num21 = 0;
		num48 = 0;
		byte[] array = File.ReadAllBytes(path);
		int num = 0;
		while (num < array.Length)
		{
			byte b = array[num];
			byte num2 = array[num + 1];
			byte b2 = array[num + 2];
			int num3 = (num2 << 8) | b2;
			int num4 = 0;
			List<byte> list = new List<byte>();
			List<byte> list2 = new List<byte>();
			byte b3 = array[num + 3];
			if (b3 % 2 != 0)
			{
				num4 = 1;
				list2.Add(b3);
				while (b3 % 2 != 0)
				{
					b3 = array[num + 3 + num4];
					list2.Add(b3);
					num4++;
				}
			}
			else
			{
				num4 = 1;
				list2.Add(b3);
			}
			for (; num4 < num3 - 3; num4++)
			{
				list.Add(array[num + 3 + num4]);
			}
			bloques++;
			num += num3;
			switch (b)
			{
			case 48:
			{
				num48++;
				Cat_048 cat_2 = new Cat_048(list2, list);
				if (cat_2.Get_Filter())
				{
					break;
				}
				if (cat_2.Get_corrected())
				{
					if (!TI.Contains(cat_2.Target__identification) && cat_2.Target__identification != "N/A")
					{
						TI.Add(cat_2.Target__identification);
						QNH.Add(cat_2.BP);
					}
				}
				else if (cat_2.Get_TBC())
				{
					string target__identification2 = cat_2.Target__identification;
					if (TI.Contains(target__identification2))
					{
						bool flag2 = false;
						int j;
						for (j = 0; j < TI.Count; j++)
						{
							if (flag2)
							{
								break;
							}
							if (target__identification2 == TI[j])
							{
								break;
							}
						}
						double value2 = Convert.ToDouble(QNH[j]);
						decimal d2 = Convert.ToDecimal(cat_2.Get_FL_double()) * 100m + (Convert.ToDecimal(value2) - Convert.ToDecimal(1013.2)) * 30m;
						cat_2.ModeC__corrected = Convert.ToString(decimal.Round(d2, 2));
						cat_2.Set_corrected(x: true);
					}
				}
				Lista_cat48.Add(cat_2);
				Lista_ASTERIX.Add(new Cat_ASTERIX(cat_2));
				break;
			}
			case 21:
			{
				num21++;
				Cat_021 cat_ = new Cat_021(list2, list);
				if (cat_.Get_filter())
				{
					break;
				}
				if (cat_.Get_corrected())
				{
					if (!TI_21.Contains(cat_.Target__identification) && cat_.Target__identification != "N/A")
					{
						TI_21.Add(cat_.Target__identification);
						QNH_21.Add(cat_.BP);
					}
				}
				else if (cat_.Get_TBC())
				{
					string target__identification = cat_.Target__identification;
					if (TI_21.Contains(target__identification))
					{
						bool flag = false;
						int i;
						for (i = 0; i < TI_21.Count; i++)
						{
							if (flag)
							{
								break;
							}
							if (target__identification == TI_21[i])
							{
								break;
							}
						}
						double value = Convert.ToDouble(QNH_21[i]);
						decimal d = Convert.ToDecimal(cat_.Get_FL_double()) * 100m + (Convert.ToDecimal(value) - Convert.ToDecimal(1013.2)) * 30m;
						cat_.ModeC__corrected = Convert.ToString(decimal.Round(d, 2));
						cat_.Set_corrected(x: true);
					}
				}
				Lista_cat21.Add(cat_);
				Lista_ASTERIX.Add(new Cat_ASTERIX(cat_));
				break;
			}
			}
		}
	}
}
