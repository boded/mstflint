/*
 * Copyright (c) 2013-2021 NVIDIA CORPORATION & AFFILIATES. ALL RIGHTS RESERVED.
 *
 * This software product is a proprietary product of Nvidia Corporation and its affiliates
 * (the "Company") and all right, title, and interest in and to the software
 * product, including all associated intellectual property rights, are and
 * shall remain exclusively with the Company.
 *
 * This software product is governed by the End User License Agreement
 * provided with the software product.
 */

#include "resource_dump_command.h"
#include "resource_dump_types.h"
#include "resource_dump_segments.h"
#include "resource_dump_error_handling.h"
#include "fetcher_factory.h"

#include <mtcr.h>
#include <cassert>

namespace mft
{
namespace resource_dump
{
using namespace std;

ResourceDumpCommand::ResourceDumpCommand(device_attributes device_attrs,
                                         dump_request dump_request,
                                         uint32_t depth,
                                         bool is_textual) :
    _mf{mopen(device_attrs.device_name)},
    _fetcher{fetchers::create_fetcher(_mf, device_attrs, dump_request, depth)},
    _is_textual{is_textual}
{
    if (_mf == nullptr)
    {
        throw ResourceDumpException(ResourceDumpException::Reason::OPEN_DEVICE_FAILED);
    }
}

ResourceDumpCommand::~ResourceDumpCommand()
{
    if (_mf)
    {
        mclose(_mf);
    }
}

void ResourceDumpCommand::execute()
{
    if (validate())
    {
        _fetcher->set_streams(_ostream, _istream);
        _fetcher->fetch_data();
        _dumped_size = _ostream->tellp();
        _fetcher->pre_parse_process();
        parse_data();
        _fetcher->post_parse_process();
        _data_fetched = true;
        if (_is_textual)
        {
            cout << *this;
        }
    }
}

void ResourceDumpCommand::parse_data()
{
    resource_dump_segment_header header_buffer{0};

    _istream->seekg(0);
    for (size_t pos = _istream->tellg(); pos < _dumped_size; pos = _istream->tellg())
    {
        _segment_offsets.push_back(pos);
        _istream->read(reinterpret_cast<char*>(&header_buffer), sizeof(resource_dump_segment_header));
        _istream->seekg(header_buffer.length_dw * 4 - sizeof(resource_dump_segment_header), istream::cur);
    }
}

const size_t ResourceDumpCommand::get_dumped_size() const
{
    return _dumped_size;
}

const bool ResourceDumpCommand::data_fetched() const
{
    return _data_fetched;
}

const std::vector<size_t>& ResourceDumpCommand::get_segment_offsets() const
{
    return _segment_offsets;
}

istream& ResourceDumpCommand::get_native_stream()
{
    if (_data_fetched)
    {
        _istream->seekg(0);
    }
    else
    {
        throw ResourceDumpException(ResourceDumpException::Reason::DATA_NOT_FETCHED);
    }
    return *_istream;
}

ostream& operator<<(ostream& out, const ResourceDumpCommand& command)
{
    if (command._is_textual && command._data_fetched)
    {
        out << command.to_string() << endl;
    }
    else
    {
        throw ResourceDumpException(ResourceDumpException::Reason::TEXT_DATA_UNAVAILABLE);
    }
    return out;
}

const string ResourceDumpCommand::to_string() const
{
    auto str = string{"Textual mode not implemented"};
    return str;
}
} // namespace resource_dump
} // namespace mft
