using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Windows;
using System.Windows.Markup;
using Microsoft.Win32;

namespace PGTA_deco048;

public partial class MainWindow : Window, IComponentConnector
{
	private Lectura decodificacion;

	private List<Cat_048> Lista_048;

	private List<Cat_ASTERIX> LF;

	private List<Cat_048> LF_48;

	private List<Cat_021> LF_21;

	private bool Only21;

	private bool Only48;

	private bool AllCat = true;

	private bool NoCat;

	public MainWindow()
	{
		InitializeComponent();
	}

	private void Button_Click(object sender, RoutedEventArgs e)
	{
		OpenFileDialog openFileDialog = new OpenFileDialog();
		openFileDialog.Filter = "Archivos asterix |*.ast";
		openFileDialog.Title = "Loading Data";
		if (openFileDialog.ShowDialog() == true)
		{
			string fileName = openFileDialog.FileName;
			decodificacion = new Lectura(fileName);
			Lista_048 = decodificacion.Lista_cat48;
			grid48.ItemsSource = decodificacion.Lista_ASTERIX;
			Visibility_objects();
			LF = decodificacion.Lista_ASTERIX;
		}
	}

	public void Visibility_objects()
	{
		grid48.Visibility = Visibility.Visible;
		button_load.Visibility = Visibility.Hidden;
		coral.Visibility = Visibility.Visible;
		cb_21.Visibility = Visibility.Visible;
		cb_48.Visibility = Visibility.Visible;
		coral.Visibility = Visibility.Visible;
		TableToCSV.Visibility = Visibility.Visible;
		reset_btn.Visibility = Visibility.Visible;
		lat_max.Visibility = Visibility.Visible;
		lat_min.Visibility = Visibility.Visible;
		lon_max.Visibility = Visibility.Visible;
		lon_min.Visibility = Visibility.Visible;
		fijo_cb.Visibility = Visibility.Visible;
		ground_cb.Visibility = Visibility.Visible;
		puro_cb.Visibility = Visibility.Visible;
		lat_label.Visibility = Visibility.Visible;
		lon_label.Visibility = Visibility.Visible;
		TI_trajectory.Visibility = Visibility.Visible;
	}

	public void Visibility_P3()
	{
		cb_21.Visibility = Visibility.Visible;
		cb_48.Visibility = Visibility.Visible;
		TableToCSV.Visibility = Visibility.Visible;
		coral.Visibility = Visibility.Hidden;
		reset_btn.Visibility = Visibility.Hidden;
		lat_max.Visibility = Visibility.Hidden;
		lat_min.Visibility = Visibility.Hidden;
		lon_max.Visibility = Visibility.Hidden;
		lon_min.Visibility = Visibility.Hidden;
		fijo_cb.Visibility = Visibility.Hidden;
		ground_cb.Visibility = Visibility.Hidden;
		puro_cb.Visibility = Visibility.Hidden;
		lat_label.Visibility = Visibility.Hidden;
		lon_label.Visibility = Visibility.Hidden;
	}

	private void coral_Click(object sender, RoutedEventArgs e)
	{
		try
		{
			double num = Convert.ToDouble(lat_min.Text);
			double num2 = Convert.ToDouble(lat_max.Text);
			double num3 = Convert.ToDouble(lon_min.Text);
			double num4 = Convert.ToDouble(lon_max.Text);
			bool flag = false;
			bool flag2 = false;
			bool flag3 = false;
			if (fijo_cb.IsChecked == true)
			{
				flag = true;
			}
			if (puro_cb.IsChecked == true)
			{
				flag2 = true;
			}
			if (ground_cb.IsChecked == true)
			{
				flag3 = true;
			}
			string text = "1";
			string text2 = "2";
			if (TI_trajectory.Text != "")
			{
				text = TI_trajectory.Text.Split(';')[0];
				text2 = TI_trajectory.Text.Split(';')[1];
			}
			if (cb_48.IsChecked == true && cb_21.IsChecked == true)
			{
				LF = new List<Cat_ASTERIX>();
				foreach (Cat_ASTERIX item in decodificacion.Lista_ASTERIX)
				{
					if ((flag == item.Get_Fijo() && flag) || (flag2 == item.Get_Puro() && flag2) || (flag3 == item.Get_Ground() && flag3) || !(item.Get_lat() < num2) || !(item.Get_lat() > num) || !(item.Get_lon() < num4) || !(item.Get_lon() > num3))
					{
						continue;
					}
					if (TI_trajectory.Text != "")
					{
						if (text == item.Target__identification || text2 == item.Target__identification)
						{
							LF.Add(item);
						}
					}
					else
					{
						LF.Add(item);
					}
				}
				grid48.ItemsSource = LF;
			}
			else if (cb_21.IsChecked == false && cb_48.IsChecked == true)
			{
				Only21 = false;
				Only48 = true;
				AllCat = false;
				NoCat = false;
				LF_48 = new List<Cat_048>();
				foreach (Cat_048 item2 in decodificacion.Lista_cat48)
				{
					if ((flag == item2.Get_Fijo() && flag) || (flag2 == item2.Get_Puro() && flag2) || (flag3 == item2.Get_Ground() && flag3) || !(item2.Get_lat() < num2) || !(item2.Get_lat() > num) || !(item2.Get_lon() < num4) || !(item2.Get_lon() > num3))
					{
						continue;
					}
					if (TI_trajectory.Text != "")
					{
						if (text == item2.Target__identification || text2 == item2.Target__identification)
						{
							LF_48.Add(item2);
						}
					}
					else
					{
						LF_48.Add(item2);
					}
				}
				grid48.ItemsSource = LF_48;
			}
			else if (cb_21.IsChecked == true && cb_48.IsChecked == false)
			{
				Only21 = true;
				Only48 = false;
				AllCat = false;
				NoCat = false;
				LF_21 = new List<Cat_021>();
				foreach (Cat_021 item3 in decodificacion.Lista_cat21)
				{
					if ((flag == item3.Get_Fijo() && flag) || (flag2 == item3.Get_Puro() && flag2) || (flag3 == item3.Get_Ground() && flag3) || !(item3.Get_lat() < num2) || !(item3.Get_lat() > num) || !(item3.Get_lon() < num4) || !(item3.Get_lon() > num3))
					{
						continue;
					}
					if (TI_trajectory.Text != "")
					{
						if (text == item3.Target__identification || text2 == item3.Target__identification)
						{
							LF_21.Add(item3);
						}
					}
					else
					{
						LF_21.Add(item3);
					}
				}
				grid48.ItemsSource = LF_21;
			}
			else
			{
				Only21 = false;
				Only48 = false;
				AllCat = false;
				NoCat = true;
				grid48.ItemsSource = decodificacion.Lista_ASTERIX;
				LF = decodificacion.Lista_ASTERIX;
				MessageBox.Show("Selecciona alguna CAT antes de filtrar", "", MessageBoxButton.OK, MessageBoxImage.Hand);
			}
		}
		catch
		{
			grid48.ItemsSource = decodificacion.Lista_ASTERIX;
			LF = decodificacion.Lista_ASTERIX;
			MessageBox.Show("Revisa los datos introducidos", "", MessageBoxButton.OK, MessageBoxImage.Hand);
			cb_21.IsChecked = true;
			cb_48.IsChecked = true;
		}
	}

	private void KML_Click(object sender, RoutedEventArgs e)
	{
	}

	private void TableToCSV_Click(object sender, RoutedEventArgs e)
	{
		SaveFileDialog saveFileDialog = new SaveFileDialog();
		saveFileDialog.Filter = "Comma separated value |*.csv";
		if (saveFileDialog.ShowDialog() == true)
		{
			string fileName = saveFileDialog.FileName;
			CSV_table(fileName);
		}
	}

	public void CSV_table(string ruta)
	{
		StringBuilder stringBuilder = new StringBuilder();
		if (AllCat)
		{
			string arg = "CAT;SAC;SIC;Time;LAT;LON;H(m);H(ft);RHO;THETA;Mode3/A;FL;TA;TI;BP;RA;TTA;GS;TAR;TAS;HDG;IAS;MACH;BAR;IVV;TN;GS(kt);HDG;STAT";
			string value = $"{arg}";
			stringBuilder.AppendLine(value);
			for (int i = 0; i < LF.Count; i++)
			{
				string text = LF[i].CAT + ";" + LF[i].SAC + ";" + LF[i].SIC + ";" + LF[i].Time + ";";
				text = text + LF[i].Latitud + ";" + LF[i].Longitud + ";" + LF[i].h__wgs84 + ";" + LF[i].h__ft + ";";
				text = text + LF[i].RHO + ";" + LF[i].THETA + ";" + Convert.ToString(LF[i].Mode__3A) + ";";
				text = text + LF[i].Flight__Level + ";" + LF[i].Target__address + ";" + LF[i].Target__identification + ";" + LF[i].BP + ";";
				text = text + LF[i].RA + ";" + LF[i].TTA + ";" + LF[i].GS + ";" + LF[i].TAR + ";" + LF[i].TAS + ";" + LF[i].HDG + ";";
				text = text + LF[i].IAS + ";" + LF[i].MACH + ";" + LF[i].BAR + ";" + LF[i].IVV + ";" + LF[i].Track__number + ";";
				text = text + LF[i].Ground__Speed_kt + ";" + LF[i].Heading + ";" + LF[i].STAT_230;
				string value2 = $"{text}";
				stringBuilder.AppendLine(value2);
			}
		}
		else if (Only21)
		{
			string arg2 = "CAT;SAC;SIC;Time;LAT;LON;H(m);H(ft);Mode3/A;FL;TA;TI;BP;RA;TTA;GS;TAR;TAS;HDG;IAS;BAR;IVV;GS(kt);HDG";
			string value3 = $"{arg2}";
			stringBuilder.AppendLine(value3);
			for (int j = 0; j < LF_21.Count; j++)
			{
				string text2 = LF_21[j].CAT + ";" + LF_21[j].SAC + ";" + LF_21[j].SIC + ";" + LF_21[j].Time + ";";
				text2 = text2 + LF_21[j].Latitud + ";" + LF_21[j].Longitud + ";" + LF_21[j].h__wgs84 + ";" + LF_21[j].h__ft + ";";
				text2 = text2 + Convert.ToString(LF_21[j].Mode__3A) + ";";
				text2 = text2 + LF_21[j].Flight__Level + ";" + LF_21[j].Target__address + ";" + LF_21[j].Target__identification + ";" + LF_21[j].BP + ";";
				text2 = text2 + LF_21[j].RA + ";" + LF_21[j].TTA + ";" + LF_21[j].GS + ";" + LF_21[j].TAR + ";" + LF_21[j].TAS + ";" + LF_21[j].HDG + ";";
				text2 = text2 + LF_21[j].IAS + ";" + LF_21[j].BAR + ";" + LF_21[j].IVV + ";";
				text2 = text2 + LF_21[j].Ground__Speed_kt + ";" + LF_21[j].Heading;
				string value4 = $"{text2}";
				stringBuilder.AppendLine(value4);
			}
		}
		else if (Only48)
		{
			string text3 = "CAT;SAC;SIC;TIME;LAT;LON;H(m);H(ft);TYP_020;SIM_020;RDP_020;SPI_020;RAB_020;TST_020;ERR_020;XPP_020;ME_020;MI_020;FOE_FRI_020;";
			text3 += "RHO;THETA;V_070;G_070;MODE 3/A;V_090;G_090;FL;SRL_130;SSR_130;SAM_130;PRL_130;PAM_130;RPD_130;APD_130;";
			text3 += "TA;TI;MCP_ALT;FMS_ALT;BP;VNAV;ALT_HOLD;APP;TARGET_ALT_SOURCE;RA;TTA;GS;TAR;TAS;HDG;IAS;MACH;BAR;IVV;TN;X;Y;GS_KT;HEADING;";
			text3 += "CNF_170;RAD_170;DOU_170;MAH_170;CDM_170;TRE_170;GHO_170;SUP_170;TCC_170;HEIGHT;COM_230;STAT_230;SI_230;MSCC_230;ARC_230;";
			text3 += "AIC_230;B1A_230;B1B_230";
			string value5 = $"{text3}";
			stringBuilder.AppendLine(value5);
			for (int k = 0; k < LF_48.Count; k++)
			{
				string text4 = LF_48[k].CAT + ";" + LF_48[k].SAC + ";" + LF_48[k].SIC + ";" + LF_48[k].Time + ";";
				text4 = text4 + LF_48[k].Latitud + ";" + LF_48[k].Longitud + ";" + LF_48[k].h__wgs84 + ";" + LF_48[k].h__ft + ";" + LF_48[k].TYP_020 + ";" + LF_48[k].SIM_020 + ";";
				text4 = text4 + LF_48[k].RDP_020 + ";" + LF_48[k].SPI_020 + ";" + LF_48[k].RAB_020 + ";" + LF_48[k].TST_020 + ";" + LF_48[k].ERR_020 + ";";
				text4 = text4 + LF_48[k].XPP_020 + ";" + LF_48[k].ME_020 + ";" + LF_48[k].MI_020 + ";" + LF_48[k].FOE_FRI_020 + ";" + LF_48[k].RHO + ";";
				text4 = text4 + LF_48[k].THETA + ";" + LF_48[k].V_070 + ";" + LF_48[k].G_070 + ";" + Convert.ToString(LF_48[k].Mode__3A) + ";" + LF_48[k].V_090 + ";";
				text4 = text4 + LF_48[k].G_090 + ";" + LF_48[k].Flight__Level + ";" + LF_48[k].SRL_130 + ";" + LF_48[k].SRR_130 + ";";
				text4 = text4 + LF_48[k].SAM_130 + ";" + LF_48[k].PRL_130 + ";" + LF_48[k].PAM_130 + ";" + LF_48[k].RPD_130 + ";" + LF_48[k].APD_130 + ";";
				text4 = text4 + LF_48[k].Target__address + ";" + LF_48[k].Target__identification + ";" + LF_48[k].MCP__ALT + ";" + LF_48[k].FMS__ALT + ";" + LF_48[k].BP + ";";
				text4 = text4 + LF_48[k].VNAV + ";" + LF_48[k].ALT_HOLD + ";" + LF_48[k].APP + ";" + LF_48[k].TARGET_ALT_SOURCE + ";" + LF_48[k].RA + ";";
				text4 = text4 + LF_48[k].TTA + ";" + LF_48[k].GS + ";" + LF_48[k].TAR + ";" + LF_48[k].TAS + ";" + LF_48[k].HDG + ";";
				text4 = text4 + LF_48[k].IAS + ";" + LF_48[k].MACH + ";" + LF_48[k].BAR + ";" + LF_48[k].IVV + ";" + LF_48[k].Track__number + ";";
				text4 = text4 + LF_48[k].X__Component + ";" + LF_48[k].Y__Component + ";" + LF_48[k].Ground__Speed_kt + ";" + LF_48[k].Heading + ";";
				text4 = text4 + LF_48[k].CNF_170 + ";" + LF_48[k].RAD_170 + ";" + LF_48[k].DOU_170 + ";" + LF_48[k].MAH_170 + ";";
				text4 = text4 + LF_48[k].CDM_170 + ";" + LF_48[k].TRE_170 + ";" + LF_48[k].GHO_170 + ";" + LF_48[k].SUP_170 + ";";
				text4 = text4 + LF_48[k].TCC_170 + ";" + LF_48[k].Measured__Height + ";" + LF_48[k].COM_230 + ";" + LF_48[k].STAT_230 + ";";
				text4 = text4 + LF_48[k].SI_230 + ";" + LF_48[k].MSCC_230 + ";" + LF_48[k].ARC_230 + ";" + LF_48[k].AIC_230 + ";";
				text4 = text4 + LF_48[k].B1A_230 + ";" + LF_48[k].B1B_230;
				string value6 = $"{text4}";
				stringBuilder.AppendLine(value6);
			}
		}
		else if (NoCat)
		{
			string arg3 = "No CAT selected";
			string value7 = $"{arg3}";
			stringBuilder.AppendLine(value7);
		}
		File.WriteAllText(ruta, stringBuilder.ToString());
		MessageBox.Show("CSV file generated", "", MessageBoxButton.OK, MessageBoxImage.Asterisk);
	}

	private void Button_Click_1(object sender, RoutedEventArgs e)
	{
		fijo_cb.IsChecked = false;
		puro_cb.IsChecked = false;
		ground_cb.IsChecked = false;
		lat_min.Text = "-90";
		lat_max.Text = "90";
		lon_min.Text = "-180";
		lon_max.Text = "180";
		grid48.ItemsSource = decodificacion.Lista_ASTERIX;
		LF = decodificacion.Lista_ASTERIX;
		LF_48 = null;
		LF_21 = null;
		cb_21.IsChecked = true;
		cb_48.IsChecked = true;
		Only21 = false;
		Only48 = false;
		AllCat = true;
		NoCat = false;
	}
}
